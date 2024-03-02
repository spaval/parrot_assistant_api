import os
import shutil

from utils.store.store import Store
from langchain_community.vectorstores import FAISS

class FaissStore(Store):
    def __init__(self, embeddings, path=os.getenv('VECTOR_STORE_LOCATION')):
        super().__init__(embeddings, path)

    def save(self, document_chunks):
        vector_index = FAISS.from_documents(document_chunks, self.embeddings)
        
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        else:
            os.makedirs(self.path)

        vector_index.save_local(self.path)

        return vector_index
    
    def load(self):
        vector_index = FAISS.load_local(self.path, self.embeddings)
        return vector_index