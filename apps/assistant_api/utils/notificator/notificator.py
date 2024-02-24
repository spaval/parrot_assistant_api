from abc import ABC, abstractclassmethod

class Notificator(ABC):
    def __init__(self):
        pass

    @abstractclassmethod
    def notify(self, text: str):
        pass