import os
import logging
import numpy as np

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

from utils.database.supabase_database import SupabaseDatabase
from utils.notificator.email_notificator import EmailNotificator
from dtos.training import Training
from utils.splitter.txt_splitter import TxtSplitter
from utils.store.faiss_store import FaissStore
from utils.ingestor.google_drive_ingestor import GoogleDriveIngestor

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_MESSAGE_ERROR = 'No se pudo obtener una respuesta por parte del asistente'

class AssistantApi(FastAPI):
    def __init__(self, **extra: any):
        super().__init__(**extra)

        env = os.getenv('env') or 'dev'
        path = f"config/.env.{env}"

        load_dotenv(path)
        self.db = self.create_data_base()

        self.add_api_route("/parrot/train", self.train, methods=["POST"])
        self.add_api_route("/parrot/query", self.query, methods=["GET"])

    async def train(self, data: Training, task: BackgroundTasks):
        task.add_task(self.process_data_sources, data.email)
            
        return {
            "error": None,
            "data": {
                "answer": "Se ha empezado el entrenamiento del asistente, una vez culminado se notificará vía correo electrónico."
            }
        }
    
    async def query(self, q, id, source, task: BackgroundTasks):
        if q is None:
            return None
        
        chat_history = ChatMessageHistory()
        
        chat_history = self.load_previous_chat_history(session_id=id, chat_history=chat_history)
        vector_store = self.create_vector_store_index()
        chain = self.create_conversational_chain(vector_store, chat_history)
        response = self.generate_assistant_response(chain, q, chat_history)

        error: str = DEFAULT_MESSAGE_ERROR
        answer: str = ''

        if response:
            error = None
            answer = response.get('answer')

            data = {
                "question": q,
                "answer": answer,
                "session_id": id,
                "source": source, 
            }

            task.add_task(self.db.save, 'history', data)

        return {
                "error": error,
                "data": {
                    "answer": answer
                }
            }
            
    def create_vector_store_index(self):
        embeddings = OpenAIEmbeddings()
        store = FaissStore(embeddings, Path(os.getenv('VECTOR_STORE_LOCATION')))
        vector_store = store.load()

        return vector_store

    def create_prompt_template(self):
        template = f'''
            Eres el bot {os.getenv('BOT_NAME')}.
            Fuiste creado para interactuar en conversaciones con humanos.
            Responde las preguntas que recibas basándote sólamente en el conocimiento que tienes.
            Si no sabes la respuesta, di que no cuentas con la información para dar respuesta a la pregunta.
            No trates de inventar una respuesta.
            Responde siempre en español con un tono amigable y acento colombiano.
            No muestres la palabra Assistant, Human, Pregunta, Respuesta en la respuesta, sólo la respuesta del asistente de forma puntual.
            Apóyate en el historial del chat para alimentar el contexto y dar respuesta a las preguntas que se te hagan.

            {{context}}
            {{chat_history}}

            {{question}}
        '''

        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )

        return prompt

    def create_conversational_chain(self, vector_store, chat_history):
        model = ChatOpenAI(
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('TEMPERATURE'),
            streaming=True,
            max_tokens=512,
        )

        prompt = self.create_prompt_template()
        memory = ConversationSummaryBufferMemory(
            llm=model,
            input_key='question',
            output_key='answer',
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=512,
            chat_memory=chat_history,
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            model,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={'k': 3}),
            combine_docs_chain_kwargs={"prompt": prompt},
            memory=memory,
            return_source_documents=True,
            verbose=False,
        )

        return chain

    def generate_assistant_response(self, chain, prompt, chat_history):
        response = chain.invoke({"question": prompt, "chat_history": chat_history})
        return response

    def load_previous_chat_history(self, session_id, chat_history):
        try:
            messages =self.db.get(
                table='history',
                filters={'session_id': session_id},
                columns='session_id, question, answer',
                order_by='created_at',
                limit=6,
            )

            if messages.data:
                for item in messages.data:
                    chat_history.add_user_message(item.get('question'))
                    chat_history.add_ai_message(item.get('answer'))

        except Exception as e:
            pass
        
        return chat_history

    def process_data_sources(self, email: str): 
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

    def create_data_base(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')

        db = SupabaseDatabase(url=url, key=key)

        return db