import os
import logging
import numpy as np

from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT

from utils.notificator.email_notificator import EmailNotificator
from dtos.training import Training
from utils.splitter.txt_splitter import TxtSplitter
from utils.store.faiss_store import FaissStore
from utils.ingestor.google_drive_ingestor import GoogleDriveIngestor

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantApi:
    app = FastAPI()

    def __init__(self, name):
        self.name = name

    @app.post("/parrot/train")
    async def train(data: Training, task: BackgroundTasks):
        task.add_task(process_data_sources, data.email)
            
        return {
            "error": None,
            "data": {
                "message": "Se ha empezado el entrenamiento del asistente, una vez culminado se notificará vía correo electrónico."
            }
        }

    @app.get("/parrot/query")
    async def query(q, id, task: BackgroundTasks):
        if q is None:
            return None
        
        chat_history = ChatMessageHistory()
        
        chat_history = load_previous_chat_history(session_id=id)
        vector_store = create_vector_store_index()
        chain = create_conversational_chain(vector_store, chat_history)
        response = generate_assistant_response(chain, q, chat_history, id, task)
        
        return {"data": response}

def create_vector_store_index():
    embeddings = OpenAIEmbeddings()
    store = FaissStore(embeddings, Path(os.getenv('VECTOR_STORE_LOCATION')))
    vector_store = store.load()

    return vector_store

def create_prompt_template():
    template = f'''
        Instrucciones:

        ¡Hola! Soy {os.getenv('BOT_NAME')}, tu asistente personal para la unidad residencial Origen P.H. Estoy aquí para ayudarte a 
        conocer todo acerca de tu hogar y facilitarte información basada en el manual de convivencia de la unidad, 
        la ley de propiedad horizontal, el código de policía, actas de asambleas y más. ¡Pregúntame lo que necesites!

        1. Manual de Convivencia:
            * ¿Cuáles son las normas de convivencia establecidas en el manual de la unidad residencial?
            * Explícame las restricciones y permisos para el uso de las áreas comunes.
        2. Ley de Propiedad Horizontal:
            * ¿Qué establece la ley de propiedad horizontal respecto a la administración y convivencia en conjuntos residenciales?
            * ¿Cuáles son los derechos y deberes de los propietarios y residentes según esta ley?
        3. Código de Policía:
            * ¿Cuáles son las normativas del código de policía que aplican específicamente a la unidad residencial?
            * ¿Qué sanciones se pueden aplicar por incumplir las normativas del código de policía en este contexto?
        4. Actas de Asambleas:
            * ¿Dónde puedo acceder a las actas de las últimas asambleas de la unidad residencial?
            * Resúmeme los puntos más importantes tratados en la última asamblea.
        5. Eventos y Actividades:
            * ¿Hay eventos o actividades próximas en la unidad residencial? Cuéntame más sobre ellas.
            * ¿Cómo puedo participar o contribuir a la organización de eventos comunitarios?
        6. Mantenimiento y Reparaciones:
            * ¿Cuál es el proceso para reportar problemas de mantenimiento en mi unidad o en áreas comunes?
            * ¿Quién es el responsable de realizar las reparaciones y cómo puedo dar seguimiento a estos procesos?

        Recuerda, estoy aquí para ayudarte y proporcionarte información precisa basada en las normativas y 
        documentos mencionados. ¡No dudes en preguntarme cualquier cosa!

        Notas:
            * Responde respuestas concisas pero completas de fácil entendimiento para un humano.
            * Responde siempre en español con un acento Colombiano.
            * Apóyate en conversaciones previas del historial.

        CONTEXTO:

        {{context}}

        PREGUNTA:

        {{question}}

        HISTORIAL:

        {{chat_history}}
    '''

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template
    )

    return prompt

def create_conversational_chain(vector_store, chat_history):
    model = ChatOpenAI(
        model_name=os.getenv('MODEL_NAME'),
        temperature=os.getenv('TEMPERATURE'),
        streaming=True,
        max_tokens=512,
    )

    prompt = create_prompt_template()
    memory = ConversationSummaryBufferMemory(
        llm=model,
        input_key='question',
        output_key='answer',
        memory_key="chat_history",
        return_messages=True,
        max_token_limit=512,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        chat_memory=chat_history,
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        model,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={'k': 3}),
        combine_docs_chain_kwargs={"prompt": prompt},
        memory=memory,
        return_source_documents=True,
        verbose=True,
    )

    return chain

def generate_assistant_response(chain, prompt, chat_history, session_id, task: BackgroundTasks):
    response = chain.invoke({"question": prompt})
    answer = response.get('answer')

    if response is not None:
        chat_history.add_user_message(prompt)
        chat_history.add_ai_message(answer)

        task.add_task(save_assistant_conversations, session_id, chat_history)

    return response

def load_previous_chat_history(session_id: str):
    folder = Path(os.getenv('MESSAGES_STORE_LOCATION'))
    path = os.path.join(folder, f'{session_id}.npy')

    chat_history = ChatMessageHistory()
    messages = []

    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                messages = np.load(f, allow_pickle=True)
    except Exception as e:
        logger.error(f"[PARROT ERRR]: {e}")
    finally:
        if messages is not None:
            for item in messages:
                if item['type'] == 'human':
                    chat_history.add_user_message(item['content'])
                elif item['type'] == 'ai':
                    chat_history.add_ai_message(item['content'])

    return chat_history

def save_assistant_conversations(session_id: str, chat_history):
    folder = Path(os.getenv('MESSAGES_STORE_LOCATION'))
    path = os.path.join(folder, f'{session_id}.npy')
    limit = int(os.getenv('MAX_MESSAGE_LIMIT'))
    
    try:
        conversation = chat_history.dict()
        if conversation:
            messages = conversation['messages']
            messages = messages[-limit:]
            
            if not(os.path.isdir(folder)):
                os.mkdir(folder)

            with open(path, "wb") as f:
                np.save(f, messages, allow_pickle=True)
    except Exception as e:
        logger.error(f"[PARROT ERRR1]: {e}")

def process_data_sources(email: str): 
    notifier = EmailNotificator(receiver=email)

    logger.info(f"[PARROT INFO]: **Training task started...**")

    try:
        ingestor = GoogleDriveIngestor()
        docs = ingestor.ingest()

        splitter = TxtSplitter(docs)
        chunks = splitter.split(size=500, overlap=100)
        
        embeddings = OpenAIEmbeddings()
        
        store = FaissStore(embeddings, Path(os.getenv('VECTOR_STORE_LOCATION')))
        store.save(chunks)

        message = "**Task Completed!**"
        logger.info(f"[PARROT INFO]: {message}")

        notifier.notify(text=message)
    except Exception as e:
        logger.error(f"[PARROT ERRR]: {e}")
        
        notifier.notify(text=e)