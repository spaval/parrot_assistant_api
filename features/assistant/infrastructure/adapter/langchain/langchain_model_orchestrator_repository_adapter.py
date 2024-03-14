import os

from langchain_openai import ChatOpenAI
from shared.splitter.txt_splitter import TxtSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from features.assistant.domain.model_orchestration_repository import ModelOrchestrationRepository
from langchain_community.chat_message_histories import ChatMessageHistory

class LangchainModelOrchestrationRepositoryAdapter(ModelOrchestrationRepository):
    def get_conversation_chain(self, vector_store, prompt_template, chat_history: ChatMessageHistory = ChatMessageHistory()):
        model = ChatOpenAI(
            openai_api_key=os.getenv('MODEL_API_KEY'),
            model_name=os.getenv('MODEL_NAME'),
            temperature=os.getenv('MODEL_TEMPERATURE'),
            streaming=os.getenv('MODEL_STREAMING'),
            max_tokens=os.getenv('MODEL_MAX_TOKENS'),
        )

        memory = ConversationBufferMemory(
            input_key='question',
            output_key='answer',
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=int(os.getenv('MODEL_MAX_TOKENS')),
            chat_memory=chat_history,
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            model,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k" : 1}),
            memory=memory,
            return_source_documents=True,
            verbose=False,
            combine_docs_chain_kwargs={
                "prompt": prompt_template,
            },
        )

        return chain
    
    def get_assistant_response(self, chain, prompt, chat_history: ChatMessageHistory = ChatMessageHistory()):
        response = chain.invoke({
            "question": prompt,
            "chat_history": chat_history.messages,
        })

        return response
    
    def get_prompt_template(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", os.getenv('MODEL_PROMPT_TEMPLATE')),
            ("human", "{question}"),
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