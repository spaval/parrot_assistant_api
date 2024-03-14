import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from shared.splitter.txt_splitter import TxtSplitter
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository
from langchain.chains import RetrievalQAWithSourcesChain

class LangchainModelOrchestrationRepositoryAdapter(ModelOrchestrationRepository):
    def get_conversation_chain(self, vector_store, prompt_template):
        model = ChatOpenAI(
            openai_api_key=os.getenv('MODEL_API_KEY'),
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('MODEL_TEMPERATURE'),
            streaming=os.getenv('MODEL_STREAMING'),
            max_tokens=os.getenv('MODEL_MAX_TOKENS'),
        )
        
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=model,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k" : 1}),
            chain_type_kwargs={
                "prompt": prompt_template,
            },
            return_source_documents=True
        )

        return chain
    
    def get_assistant_response(self, chain, prompt):
        response = chain.invoke({"question": prompt}, return_only_outputs=True)
        return response
    
    def get_prompt_template(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", os.getenv('MODEL_PROMPT_TEMPLATE')),
        ])

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