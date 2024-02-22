import os

from pathlib import Path
from fastapi import FastAPI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain

from utils.ingestor.pdf_ingestor import PDFIngestor
from utils.splitter.txt_splitter import TxtSplitter
from utils.store.faiss_store import FaissStore

class AssistantApi:
    app = FastAPI()

    def __init__(self, name):
        self.name = name

    @app.post("/parrot/train")
    async def train():
        ingestor = PDFIngestor([
            Path(os.getenv('DATA_STORE_LOCATION'))
        ])
        docs = ingestor.ingest()

        splitter = TxtSplitter(docs)
        chunks = splitter.split(size=500, overlap=100)
        
        embeddings = OpenAIEmbeddings()
        
        store = FaissStore(embeddings, Path(os.getenv('VECTOR_STORE_LOCATION')))
        index = store.save(chunks)

        result: bool

        if index is None:
            result = False
        
        result = True

        return {"trained": result, "source": docs}

    @app.get("/parrot/query")
    async def query(q: str | None = None):
        if q is None:
            return None
        
        embeddings = OpenAIEmbeddings()
        store = FaissStore(embeddings, Path(os.getenv('VECTOR_STORE_LOCATION')))
        vector_store = store.load()

        model = ChatOpenAI(
            model_name=Path(os.getenv('MODEL_NAME')),
            temperature=Path(os.getenv('TEMPERATURE')),
            streaming=True
        )

        system_message = '''
            Eres el bot Parrot.
            Fuiste creado para interactuar en conversaciones con humanos.
            Responde las preguntas que recibas basándote sólamente en el conocimiento que tienes.
            Si no sabes la respuesta, di que no cuentas con la información para dar respuesta a la pregunta, no trates de inventar una respuesta.
            Responde siempre en español con un tono amigable y acento colombiano.

            {summaries}

            Pregunta: {question}
        '''

        prompt = PromptTemplate(
            template=system_message,
            input_variables=["summaries", "question"],
        )

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=model,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={'k': 3}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        result = chain({"question": q}, return_only_outputs=True)
        response = dict()

        response.update({"answer": result['answer']})
        sources = []

        for item in result['source_documents']:
            if item.metadata['source']:
                sources.append(item.metadata['source'])

        response.update({"sources": list(dict.fromkeys(sources))})

        return {"data": response}