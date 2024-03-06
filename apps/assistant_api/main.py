import uvicorn

from app import AssistantApi
from feature.assistant.application.assistance_service import AssistantService
from feature.assistant.infrastructure.adapter.google_drive.google_drive_repository_adapter import GoogleDriveRepositoryAdapter
from feature.assistant.infrastructure.adapter.langchain.langchain_conversation_repository_adapter import LangchainConversationRepositoryAdapter
from feature.assistant.infrastructure.adapter.supabase.supabase_database_repository_adapter import SupabaseDatabaseRepositoryAdapter
from feature.assistant.infrastructure.adapter.supabase.supabase_vector_store_repository_adapter import SupabaseVectorStoreRepositoryAdapter
from feature.assistant.infrastructure.entrypoint.rest.handler.assistant_handler import AssistantHandler

def main():
    service = AssistantService(
        vector_store_repository=SupabaseVectorStoreRepositoryAdapter(),
        database_repository=SupabaseDatabaseRepositoryAdapter(),
        ingestor_repository=GoogleDriveRepositoryAdapter(),
        model_orchestration_repository=LangchainConversationRepositoryAdapter(),
    )

    handler = AssistantHandler(service=service)
    AssistantApi(handler=handler)

    uvicorn.run(
        'app:AssistantApi',
        host="0.0.0.0",
        port=8000,
        reload=True,      
        log_level="info",
        loop="asyncio",
        factory=True,
    )
    
if __name__ == '__main__':
    main()