from abc import ABC, abstractclassmethod

class VectorStoreRepository(ABC):
    @abstractclassmethod
    def load(self):
        pass

    @abstractclassmethod
    def save(self, chunks):
        pass