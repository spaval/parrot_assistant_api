from abc import ABC, abstractclassmethod

class Database(ABC):
    def __init__(self):
        pass

    def connect(self):
        pass

    def get(self, table, columns, filters):
        pass

    def save(self, table, data):
        pass

    def delete(self, table, id, key):
        pass

    def update(self, table, data, id, key):
        pass

    def close(self):
        pass