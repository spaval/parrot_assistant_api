
import os

from shared.ingestor.shopify_ingestor import ShopifyIngestor
from features.assistant.domain.ingestor_repository import IngestorRepository

class ShopifyRepositoryAdapter(IngestorRepository):
    def ingest(self):
        config = {
            "api_version": os.getenv('SHOPIFY_API_VERSION'),
            "store_url": os.getenv('SHOPIFY_STORE_URL'),
            "api_key": os.getenv('SHOPIFY_API_KEY'),
            "resource": os.getenv('SHOPIFY_RESOURCE'),
        }

        ingestor = ShopifyIngestor(
            config=config,
        )

        return ingestor.ingest()