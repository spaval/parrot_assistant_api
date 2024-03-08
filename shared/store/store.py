from abc import ABC, abstractclassmethod

class Store(ABC):
    @abstractclassmethod
    def __init__(self, embeddings, path):
        self.embeddings = embeddings
        self.path = path

    @abstractclassmethod
    def save(self):
        pass

    @abstractclassmethod
    def load(self):
        pass