import os
import logging

from features.assistant.domain.database_repository import DatabaseRepository
from features.assistant.domain.ingestor_repository import IngestorRepository
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository
from features.assistant.domain.vector_store_repository import VectorStoreRepository

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantService:
    def __init__(
        self,
        vector_store_repository: VectorStoreRepository,
        database_repository: DatabaseRepository,
        ingestor_repository: IngestorRepository,
        model_orchestration_repository: ModelOrchestrationRepository,
    ):
        self.vector_store_repository = vector_store_repository
        self.database_repository = database_repository
        self.ingestor_repository = ingestor_repository
        self.model_orchestration_repository = model_orchestration_repository
        
    def train(self, email: str): 
        logger.info(f"[{os.getenv('BOT_NAME')}]: **Training started...**")

        try:
            docs = self.ingestor_repository.ingest()
            chunks = self.model_orchestration_repository.get_splitted_documents(
                docs,
                size=int(os.getenv('DOCUMENTS_SPLITTED_SIZE')),
                overlap=int(os.getenv('DOCUMENTS_SPLITTED_OVERLAP'))
            )
            self.vector_store_repository.save(chunks)

            logger.info(f"[{os.getenv('BOT_NAME')}]: **Training Completed!**")

        except Exception as e:
            logger.error(f"[{os.getenv('BOT_NAME')}]: {e}")

    def query(self, q, id, source, task):
        response = dict()

        try:
            vector_store = self.vector_store_repository.load()
            prompt_template = self.model_orchestration_repository.get_prompt_template()
            chain = self.model_orchestration_repository.get_conversation_chain(vector_store, prompt_template)

            messages = self.database_repository.get_chat_messages(session_id=id)
            chat_history = self.model_orchestration_repository.get_chat_history(messages)

            response = self.model_orchestration_repository.get_assistant_response(chain, q, chat_history)

            data = {
                "question": q,
                "answer": response.get('answer'),
                "session_id": id,
                "source": source, 
            }

            task.add_task(self.database_repository.save, os.getenv('CHATS_TABLE_NAME'), data)

        except Exception as e:
            logger.error(f"[{os.getenv('BOT_NAME')}]: {e}")

        return response