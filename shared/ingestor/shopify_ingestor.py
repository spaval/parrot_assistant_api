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
                status = doc.metadata.get('status')
                if status == 'active':
                    doc.page_content = get_title(doc)

        return docs
    
def get_title(doc):
    title: str = ''
    variants = doc.metadata['variants']

    if variants:
        extra = variants[0]
        title = f"Producto: {doc.metadata['title']} | Precio: {int(extra['price'])} | ID: {extra['product_id']} | Peso: {extra['weight']}{extra['weight_unit']} | SKU: {extra['sku']}"

    return title
