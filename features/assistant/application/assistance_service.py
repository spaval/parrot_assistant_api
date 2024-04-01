import os
import logging
import re
import json

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
        
    async def train(self, data): 
        logger.info(f"[{os.getenv('BOT_NAME')}]: **Training started...**")

        try:
            docs = self.ingestor_repository.ingest()
            chunks = []

            if len(docs) > 0:
                chunks = self.model_orchestration_repository.get_splitted_documents(
                    docs,
                    size=int(os.getenv('DOCUMENTS_SPLITTED_SIZE')),
                    overlap=int(os.getenv('DOCUMENTS_SPLITTED_OVERLAP')),
                    separators=os.getenv('DOCUMENTS_SPLITTED_SEPARATORs'),
                )

            if len(chunks) > 0:
                self.vector_store_repository.save(chunks)

            logger.info(f"[{os.getenv('BOT_NAME')}]: **Training Completed!**")

        except Exception as e:
            logger.error(f"[{os.getenv('BOT_NAME')}]: {e}")
    
    async def query(self, data, task):
        vector_store = self.vector_store_repository.load()

        if data.get('mode') == HistoryModeEnum.db:
            messages = self.database_repository.get_chat_messages(conversation_id=data.get('conversation_id'))
            chat_history = self.model_orchestration_repository.get_chat_history(messages.data or [])
        else:
            messages = get_cached_data(data.get('conversation_id'))
            chat_history = self.model_orchestration_repository.get_chat_history(messages or [])

        data["chat_history"] = chat_history

        prompt = self.model_orchestration_repository.get_prompt_template()
        response = await self.model_orchestration_repository.get_assistant_response(
            prompt,
            vector_store,
            data
        )
        
        if response:
            info = {
                "question": data.get('question'),
                "answer": response.get('answer'), 
            }

            if data.get('mode') == HistoryModeEnum.db:
                task.add_task(
                    self.database_repository.save_chat_messages,
                    os.getenv('CHATS_TABLE_NAME'),
                    info
                )
            else:
                task.add_task(
                    save_data_to_cache,
                    data.get('conversation_id'),
                    info
                )

        return response
    
    async def shop(self, data, task):
        vector_store = self.vector_store_repository.load()

        messages = get_cached_data(cache_key=data.get('conversation_id'))
        chat_history = self.model_orchestration_repository.get_chat_history(messages)

        data["chat_history"] = chat_history

        prompt = self.model_orchestration_repository.get_prompt_template()
        response = await self.model_orchestration_repository.get_assistant_response(
            prompt,
            vector_store,
            data
        )

        if response:
            answer = response.get('answer')
            match = re.search(r'```json\n(.+?)```', answer, re.DOTALL)

            if match:
                json_str = match.group(1).strip()
            
                # TODO: save order into db
                order = json.loads(json_str)
            
                clean_answer = re.sub(r'```json\n(.+?)```', '', answer, flags=re.DOTALL)
                response['answer'] = clean_answer

            info = {
                "question": data.get('question'),
                "answer": response.get('answer'),
            }

            task.add_task(
                save_data_to_cache,
                data.get('conversation_id'),
                info
            )

        return response