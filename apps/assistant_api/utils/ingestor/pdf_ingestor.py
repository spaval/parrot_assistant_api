from utils.ingestor.ingestor import Ingestor
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

class PDFIngestor(Ingestor):
    def __init__(self, path = []):
        super().__init__(path)

    def ingest(self):
        if self.path is None:
            return None
        
        loader = DirectoryLoader(
            self.path[0],
            glob="**/*.pdf",
            use_multithreading=True,
            recursive=True,
            loader_cls=PyPDFLoader,
            silent_errors=True
        )
        
        docs = loader.load()

        return docs
    

    
