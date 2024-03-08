from langchain_openai import OpenAIEmbeddings

from shared.store.faiss_store import FaissStore
from features.assistant.domain.vector_store_repository import VectorStoreRepository

class SupabaseVectorStoreRepositoryAdapter(VectorStoreRepository):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()

    def load(self):
        store = FaissStore(self.embeddings)
        return store.load()
    
    def save(self, chunks):
        store = FaissStore(self.embeddings)
        store.save(chunks)