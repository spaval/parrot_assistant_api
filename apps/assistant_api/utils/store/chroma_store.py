import chromadb
import cloudpickle
import os
import shutil

from utils.store.store import Store

class ChromaStore(Store):
    def __init__(self, document_chunks, embeddings, path):
        super().__init__(document_chunks, embeddings, path)

    def save(self):
        vector_index = chromadb.from_documents(documents=self.document_chunks, embedding=self.embeddings)

        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        else:
            os.makedirs(self.path)

        with open(self.path, "wb") as f:
            cloudpickle.dump(vector_index, f)

        return vector_index
    
    def load(self):
        with open(self.path, "rb") as f:
            vector_index = cloudpickle.load(f)

        return vector_index