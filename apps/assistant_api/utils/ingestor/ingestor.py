from abc import ABC, abstractclassmethod

class Ingestor(ABC):
    @abstractclassmethod
    def __init__(self, path):
        self.path = path

    @abstractclassmethod
    def ingest(self):
        pass