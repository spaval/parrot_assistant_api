import os

from utils.database.database import Database
from supabase import create_client, Client

class SupabaseDatabase(Database):
    def __init__(self):
        super().__init__()
        self.client: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

    def connect(self):
        pass

    def get(self, table, columns='*', order_by=None, filters={}, limit=5):
        clt = self.client.table(table).select(columns.join(','))
        if filters:
            for key, value in filters.items():
                clt.eq(key, value)

        if order_by:
            clt.order(order_by, desc=True)

        if limit:
            clt.limit(limit)
            
        response = clt.execute()
        return response

    def save(self, table, data):
        response = self.client.table(table).insert(data).execute()
        return response

    def delete(self, table, id, key='id'):
        response = self.client.table(table).delete().eq(key, id).execute()
        return response

    def update(self, table, data, id, key='id'):
        response = self.client.table(table).update(data).eq(key, id).execute()
        return response

    def close(self):
        pass