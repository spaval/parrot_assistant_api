import os

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from langchain_community.vectorstores import SupabaseVectorStore

from utils.store.store import Store

class SupabaseStore(Store):
    def __init__(self, embeddings, path=os.getenv('VECTOR_STORE_LOCATION')):
        super().__init__(embeddings, path)

        options = ClientOptions(postgrest_client_timeout=None)
        self.client: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'), options=options)

    def save(self, document_chunks):
        vectorstore = SupabaseVectorStore.from_documents(
            document_chunks,
            self.embeddings,
            client=self.client,
            table_name=os.getenv('DOCUMENTS_TABLE_NAME'),
            query_name="match_documents",
            chunk_size=int(os.getenv('DOCUMENTS_CHUNK_SIZE')),
        )

        return vectorstore
    
    def load(self):
        vector_store = SupabaseVectorStore(
            embedding=self.embeddings,
            client=self.client,
            table_name=os.getenv('DOCUMENTS_TABLE_NAME'),
            query_name="match_documents",
        )

        return vector_store