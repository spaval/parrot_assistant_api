from utils.ingestor.ingestor import Ingestor
from langchain_community.document_loaders import WebBaseLoader

class URLIngestor(Ingestor):
    def __init__(self, path):
        super().__init__(path)

    def ingest(self):
        if self.path is None:
            return None
        
        loader = WebBaseLoader(self.path)
        
        docs = loader.load()

        return docs