from utils.ingestor.ingestor import Ingestor
from langchain_community.document_loaders.airbyte import AirbyteShopifyLoader

class ShopifyIngestor(Ingestor):
    def __init__(self, config, stream_name):
        super().__init__('')
        
        self.config = config
        self.stream_name = stream_name

    def ingest(self):
        if self.config is None:
            return None
        
        last_state = loader.last_state

        loader = AirbyteShopifyLoader(
            config=self.config,
            stream_name=self.stream_name,
            state=last_state,
        )

        docs = loader.load()

        return docs