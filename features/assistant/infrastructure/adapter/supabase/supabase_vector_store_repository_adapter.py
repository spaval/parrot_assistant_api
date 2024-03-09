import os

<<<<<<< HEAD
from langchain_openai import OpenAIEmbeddings
=======
>>>>>>> develop
from shared.store.supabase_store import SupabaseStore
from features.assistant.domain.vector_store_repository import VectorStoreRepository

class SupabaseVectorStoreRepositoryAdapter(VectorStoreRepository):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('MODEL_API_KEY'))

    def load(self):
        store = SupabaseStore(self.embeddings)
        return store.load()
    
    def save(self, chunks):
        store = SupabaseStore(self.embeddings)
        store.save(chunks)