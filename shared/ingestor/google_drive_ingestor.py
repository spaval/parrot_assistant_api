import os

from shared.ingestor.ingestor import Ingestor
from langchain_community.document_loaders import GoogleDriveLoader, UnstructuredFileIOLoader

class GoogleDriveIngestor(Ingestor):
    def __init__(self, file_types: list[str] = os.getenv('SUPPORTED_FILE_TYPES')):
        super().__init__('')

        self.file_types = file_types
        self.credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH')

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials

    def ingest(self):
        loader = GoogleDriveLoader(
            folder_id=os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
            credentials_path=self.credentials,
            token_path=os.getenv('GOOGLE_DRIVE_TOKEN_PATH'),
            recursive=True,
            file_loader_cls=UnstructuredFileIOLoader,
            file_loader_kwargs={"mode": "elements"}
        )
        
        docs = loader.load()

        for doc in docs:
            doc.metadata = {
                "source": doc.metadata.get('title'),
                "url": doc.metadata.get('source'),
                "page": doc.metadata.get('page_number'),
            }

        return docs
    

    
