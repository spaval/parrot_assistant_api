from abc import ABC, abstractclassmethod

class ModelOrchestrationRepository(ABC):
    @abstractclassmethod
    def get_chat_history(self, messages: list[any]):
        pass

    @abstractclassmethod
    def get_prompt_template(self):
        pass

    @abstractclassmethod
    def get_splitted_documents(self, docs, **kwargs):
        pass

    @abstractclassmethod
    async def get_assistant_response(self, prompt, vector_store, data):
        pass