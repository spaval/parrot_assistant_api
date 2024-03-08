from shared.ingestor.ingestor import Ingestor
from langchain_community.document_loaders.airbyte import AirbyteShopifyLoader

class ShopifyIngestor(Ingestor):
    def __init__(self, config, stream_name):
        super().__init__('')
        
        self.config = config
        self.stream_name = stream_name

    def ingest(self):
        if self.config is None:
            return None

        loader = AirbyteShopifyLoader(
            config=self.config,
            stream_name=self.stream_name,
        )
        
        docs = loader.load()

        if docs:
            for doc in docs:
                doc.page_content = get_title(doc)

        return docs
    
def get_title(doc):
    title: str = ''
    variants = doc.metadata['variants']

    if variants:
        extra = variants[0]
        title = f"Product: {doc.metadata['title']} - Price: {extra['price']} - ProductId: {extra['product_id']} - Size: {extra['weight']}{extra['weight_unit']}"

    return title
