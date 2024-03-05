import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain

from utils.database.supabase_database import SupabaseDatabase
from dtos.training import Training
from utils.splitter.txt_splitter import TxtSplitter
from utils.store.supabase_store import SupabaseStore
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
        vector_store = self.load_vector_store_index()

        chain = self.create_conversational_chain(vector_store)
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

            task.add_task(self.db.save, os.getenv('CHATS_TABLE_NAME'), data)

        return {
            "error": error,
            "data": {
                "answer": answer
            }
        }
            
    def load_vector_store_index(self):
        embeddings = OpenAIEmbeddings()
        store = SupabaseStore(embeddings)
        vector_store = store.load()

        return vector_store

    def create_prompt_template(self):
        prompt = ChatPromptTemplate.from_template(os.getenv('MODEL_PROMPT_TEMPLATE'))
        return prompt

    def create_conversational_chain(self, vector_store):
        '''model = ChatOpenAI(
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('MODEL_TEMPERATURE'),
            streaming=True,
            max_tokens=512,
        )'''
        model = ChatGroq(
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('MODEL_TEMPERATURE'),
        )

        prompt = self.create_prompt_template()
        document_chain = create_stuff_documents_chain(model, prompt)

        retrieval_chain = create_retrieval_chain(
            vector_store.as_retriever(),
            document_chain,
        )

        return retrieval_chain

    def generate_assistant_response(self, chain, prompt, chat_history):
        response = chain.invoke({"input": prompt, "chat_history": chat_history})
        return response

    def load_previous_chat_history(self, session_id, chat_history):
        try:
            messages =self.db.get(
                table=os.getenv('CHATS_TABLE_NAME'),
                filters={'session_id': session_id},
                columns='session_id, question, answer',
                order_by='created_at',
                limit=os.getenv('MAX_MESSAGE_LIMIT'),
            )

            if messages.data:
                for item in messages.data:
                    chat_history.add_user_message(item.get('question'))
                    chat_history.add_ai_message(item.get('answer'))

        except Exception as e:
            pass
        
        return chat_history

    def create_data_base(self):
        db = SupabaseDatabase()
        return db
    
    def process_data_sources(self, email: str): 
        logger.info(f"[PARROT INFO]: **Training task started...**")

        try:
            ingestor = GoogleDriveIngestor()
            docs = ingestor.ingest()
            
            splitter = TxtSplitter(docs)
            chunks = splitter.split(size=500, overlap=100)
            
            embeddings = OpenAIEmbeddings()

            store = SupabaseStore(embeddings)
            store.save(chunks)

            message = "**Task Completed!**"
            logger.info(f"[PARROT INFO]: {message}")

        except Exception as e:
            logger.error(f"[PARROT ERRR]: {e}")