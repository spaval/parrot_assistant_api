
import os

from shared.ingestor.shopify_ingestor import ShopifyIngestor
from features.assistant.domain.ingestor_repository import IngestorRepository

class ShopifyRepositoryAdapter(IngestorRepository):
    def ingest(self):
        config = {
            "start_date": os.getenv('SHOPIFY_START_DATE'),
            "shop": os.getenv('SHOPIFY_STORE'),
            "credentials": {
                "auth_method": os.getenv('SHOPIFY_AUTH_METHOD'),
                "access_token": os.getenv('SHOPIFY_ACCESS_TOKEN'),
            }
        }

        ingestor = ShopifyIngestor(
            config=config,
            stream_name=os.getenv('SHOPIFY_RESOURCE'),
        )

        return ingestor.ingest()