

from shared.ingestor.google_drive_ingestor import GoogleDriveIngestor
from features.assistant.domain.ingestor_repository import IngestorRepository

class GoogleDriveRepositoryAdapter(IngestorRepository):
    def ingest(self):
        ingestor = GoogleDriveIngestor()
        return ingestor.ingest()