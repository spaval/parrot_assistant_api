import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain

from shared.splitter.txt_splitter import TxtSplitter
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository

class LangchainModelOrchestrationRepositoryAdapter(ModelOrchestrationRepository):
    def get_conversation_chain(self, vector_store, prompt_template):
        model = ChatGroq(
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('MODEL_TEMPERATURE'),
            streaming=os.getenv('MODEL_STREAMING'),
            max_tokens=os.getenv('MODEL_MAX_TOKENS'),
        )

        document_chain = create_stuff_documents_chain(model, prompt_template)

        retrieval_chain = create_retrieval_chain(
            vector_store.as_retriever(),
            document_chain,
        )

        return retrieval_chain
    
    def get_assistant_response(self, chain, prompt, chat_history):
        response = chain.invoke({"input": prompt, "chat_history": chat_history})
        return response
    
    def get_prompt_template(self):
        prompt = ChatPromptTemplate.from_template(os.getenv('MODEL_PROMPT_TEMPLATE'))
        return prompt
    
    def get_chat_history(self, messages):
        chat_history = ChatMessageHistory()

        if messages.data:
            for item in messages.data:
                chat_history.add_user_message(item.get('question'))
                chat_history.add_ai_message(item.get('answer'))

        return chat_history
    
    def get_splitted_documents(self, docs, **kwargs):
        splitter = TxtSplitter(docs)
        chunks = splitter.split(**kwargs)
        
        return chunks