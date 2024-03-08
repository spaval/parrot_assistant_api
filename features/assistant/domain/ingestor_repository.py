from abc import ABC, abstractclassmethod

class IngestorRepository(ABC):
    @abstractclassmethod
    def ingest(self):
        pass