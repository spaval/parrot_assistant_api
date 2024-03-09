from shared.splitter.splitter import Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TxtSplitter(Splitter):
    def __init__(self, documents):
        super().__init__(documents)

    def split(self, size=500, overlap=100, separator="\n"):
        text_sppliter = RecursiveCharacterTextSplitter(
            separators=[separator],
            chunk_size=int(size),
            chunk_overlap=int(overlap),
            length_function=len
        )

        chunks = text_sppliter.split_documents(self.documents)

        return chunks