from abc import ABC, abstractclassmethod

class Splitter(ABC):
    @abstractclassmethod
    def __init__(self, documents):
        self.documents = documents

    @abstractclassmethod
    def split(self):
       pass