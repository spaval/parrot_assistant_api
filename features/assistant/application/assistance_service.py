import os
import logging

from features.assistant.domain.database_repository import DatabaseRepository
from features.assistant.domain.ingestor_repository import IngestorRepository
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository
from features.assistant.domain.vector_store_repository import VectorStoreRepository
from features.assistant.infrastructure.entrypoint.rest.handler.dto.query import HistoryModeEnum
from shared.helpers.cache import get_cached_data, save_data_to_cache

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
        
    def train(self, data): 
        logger.info(f"[{os.getenv('BOT_NAME')}]: **Training started...**")

        try:
            docs = self.ingestor_repository.ingest()
            
            chunks = self.model_orchestration_repository.get_splitted_documents(
                docs,
                size=int(os.getenv('DOCUMENTS_SPLITTED_SIZE')),
                overlap=int(os.getenv('DOCUMENTS_SPLITTED_OVERLAP')),
                separators=os.getenv('DOCUMENTS_SPLITTED_SEPARATORs'),
            )

            self.vector_store_repository.save(chunks)

            logger.info(f"[{os.getenv('BOT_NAME')}]: **Training Completed!**")

        except Exception as e:
            logger.error(f"[{os.getenv('BOT_NAME')}]: {e}")

    def query(self, data, task):
        response = dict()

        try:
            chat_history = []
            vector_store = self.vector_store_repository.load()

            if data.history_mode == HistoryModeEnum.db:
                messages = self.database_repository.get_chat_messages(conversation_id=data.conversation_id)
                chat_history = self.model_orchestration_repository.get_chat_history(messages.data or [])
            else:
                messages = get_cached_data(data.conversation_id)
                chat_history = self.model_orchestration_repository.get_chat_history(messages or [])

            prompt_template = self.model_orchestration_repository.get_prompt_template()
            chain = self.model_orchestration_repository.get_conversation_chain(vector_store, prompt_template, chat_history)
            response = self.model_orchestration_repository.get_assistant_response(chain, data.question, chat_history)
            
            info = {
                "question": data.question,
                "answer": response.get('answer'),
                "conversation_id": data.conversation_id,
                "source": data.platform_source, 
            }

            if data.history_mode == HistoryModeEnum.db:
                task.add_task(self.database_repository.save_chat_messages, os.getenv('CHATS_TABLE_NAME'), info)
            else:
                task.add_task(save_data_to_cache, data.conversation_id, info)

        except Exception as e:
            logger.error(f"[{os.getenv('BOT_NAME')}]: {e}")

        return response