import os

from langchain_openai import OpenAIEmbeddings
from shared.store.faiss_store import FaissStore
from features.assistant.domain.vector_store_repository import VectorStoreRepository

class FaissVectorStoreRepositoryAdapter(VectorStoreRepository):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('MODEL_API_KEY'))

    def load(self):
        store = FaissStore(self.embeddings)
        return store.load()
    
    def save(self, chunks):
        store = FaissStore(self.embeddings)
        store.save(chunks)