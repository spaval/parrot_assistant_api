import os

from shared.database.supabase_database import SupabaseDatabase
from features.assistant.domain.database_repository import DatabaseRepository

class SupabaseDatabaseRepositoryAdapter(DatabaseRepository):
    def __init__(self):
        self.db = SupabaseDatabase()
        
    def save_chat_messages(self, table, data):
        return self.db.save(table, data)
    
    def get_chat_messages(self, conversation_id):
        messages = []

        try:
            messages = self.db.get(
                table=os.getenv('CHATS_TABLE_NAME'),
                filters={'conversation_id': conversation_id},
                columns='conversation_id, question, answer',
                order_by='created_at',
                limit=os.getenv('MAX_MESSAGE_LIMIT'),
            )

        except Exception as e:
            pass

        return messages