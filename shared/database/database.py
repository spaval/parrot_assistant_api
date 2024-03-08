from abc import ABC, abstractclassmethod

class Database(ABC):
    @abstractclassmethod
    def __init__(self):
        pass

    @abstractclassmethod
    def connect(self):
        pass

    @abstractclassmethod
    def get(self, table, columns, filters):
        pass

    @abstractclassmethod
    def save(self, table, data):
        pass

    @abstractclassmethod
    def delete(self, table, id, key):
        pass

    @abstractclassmethod
    def update(self, table, data, id, key):
        pass

    @abstractclassmethod
    def close(self):
        pass