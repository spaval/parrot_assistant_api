from abc import ABC, abstractclassmethod

class DatabaseRepository(ABC):
    @abstractclassmethod
    def save_chat_messages(self, table, data):
        pass

    @abstractclassmethod
    def get_chat_messages(self, conversation_id):
        pass
