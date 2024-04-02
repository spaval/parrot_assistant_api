import uvicorn
from fastapi import FastAPI
from shared.helpers.version import get_api_version
from features.assistant.application.assistance_service import AssistantService
from features.assistant.infrastructure.entrypoint.rest.handler.assistant_handler import AssistantHandler
from features.assistant.infrastructure.adapter.shopify.shopify_repository_adapter import ShopifyRepositoryAdapter
from features.assistant.infrastructure.adapter.google_drive.google_drive_repository_adapter import GoogleDriveRepositoryAdapter
from features.assistant.infrastructure.adapter.langchain.langchain_model_orchestrator_repository_adapter import LangchainModelOrchestrationRepositoryAdapter
from features.assistant.infrastructure.adapter.supabase.supabase_database_repository_adapter import SupabaseDatabaseRepositoryAdapter
from features.assistant.infrastructure.adapter.faiss.faiss_vector_store_repository_adapter import FaissVectorStoreRepositoryAdapter

class App(FastAPI):
    def __init__(self, **kwargs: any):
        super().__init__(**kwargs)

        api_version = get_api_version('Makefile', 'VERSION')
        
        assistant_service = AssistantService(
            vector_store_repository=FaissVectorStoreRepositoryAdapter(),
            database_repository=SupabaseDatabaseRepositoryAdapter(),
            #ingestor_repository=ShopifyRepositoryAdapter(),
            ingestor_repository=GoogleDriveRepositoryAdapter(),
            model_orchestration_repository=LangchainModelOrchestrationRepositoryAdapter(),
        )

        self.handler = AssistantHandler(service=assistant_service)
        
        self.add_event_handler("startup", self.handler.on_startup)
        self.add_api_route(f"/v{api_version}/train", self.handler.train, methods=["POST"])
        self.add_api_route(f"/v{api_version}/query", self.handler.query, methods=["POST"])
        self.add_api_route(f"/v{api_version}/shop", self.handler.shop, methods=["POST"])

    def run(self):
        uvicorn.run(
            f"{self.__class__.__module__}:{self.__class__.__name__}",
            host="0.0.0.0",
            port=8000,
            reload=True,      
            log_level="info",
            loop="asyncio",
            factory=True,
        )
        