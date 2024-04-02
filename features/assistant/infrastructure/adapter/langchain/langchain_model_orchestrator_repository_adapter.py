import os

from langchain_openai import ChatOpenAI
from shared.splitter.txt_splitter import TxtSplitter
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

class LangchainModelOrchestrationRepositoryAdapter(ModelOrchestrationRepository):   
    def get_chat_history(self, messages: list[any]):
        chat_history = ChatMessageHistory()

        if messages:
            for item in messages:
                chat_history.add_user_message(item.get('question'))
                chat_history.add_ai_message(item.get('answer'))

        return chat_history

    def get_prompt_template(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", os.getenv("MODEL_SYSTEM_TEMPLATE")),
            MessagesPlaceholder(variable_name="chat_history"),
        ])

        return prompt

    def get_splitted_documents(self, docs, **kwargs):
        splitter = TxtSplitter(docs)
        chunks = splitter.split(**kwargs)
        
        return chunks

    async def get_assistant_response(self, prompt, vector_store, data):
        data.get('chat_history').add_user_message(data.get('question'))

        chat = ChatOpenAI(
            openai_api_key=os.getenv('MODEL_API_KEY'),
            model=os.getenv('MODEL_NAME'),
            temperature=float(os.getenv('MODEL_TEMPERATURE')),
        )

        retriever = vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k" : 3})

        query_transforming_retriever_chain = RunnableBranch(
            (
                lambda x: len(x.get("chat_history", [])) > 0,
                (lambda x: x["chat_history"][-1].content) | retriever,
            ),
            prompt | chat | StrOutputParser() | retriever,
        ).with_config(run_name="chat_retriever_chain")

        documents_chain = create_stuff_documents_chain(chat, prompt)

        retrieval_chain = RunnablePassthrough.assign(
            context=query_transforming_retriever_chain,
        ).assign(
            answer=documents_chain,
        )

        response = await retrieval_chain.ainvoke({
            "chat_history": data.get('chat_history').messages,
        })

        return response