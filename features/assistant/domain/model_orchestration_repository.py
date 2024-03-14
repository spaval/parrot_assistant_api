from abc import ABC, abstractclassmethod

class ModelOrchestrationRepository(ABC):
    @abstractclassmethod
    def get_conversation_chain(self, vector_store, prompt_template, chat_history):
        pass

    @abstractclassmethod
    def get_prompt_template(self):
        pass

    @abstractclassmethod
    def get_assistant_response(self, chain, prompt, chat_history):
        pass

    @abstractclassmethod
    def get_chat_history(self, messages):
        pass

    @abstractclassmethod
    def get_splitted_documents(self, docs, **kwargs):
        pass