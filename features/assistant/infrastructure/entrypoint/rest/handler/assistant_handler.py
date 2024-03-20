from features.assistant.application.assistance_service import AssistantService
from features.assistant.infrastructure.entrypoint.rest.handler.dto.query import QueryResponse, QueryResponseData, QueryResponseError
from features.assistant.infrastructure.entrypoint.rest.handler.dto.training import TrainingRequest
from features.assistant.infrastructure.entrypoint.rest.handler.dto.query import QueryRequest, QueryModeEnum
from shared.helpers.contains import contains
from shared.url_shortener.url_shortener import short

from fastapi import BackgroundTasks

DEFAULT_MESSAGE_ERROR = 'No se pudo obtener una respuesta por parte del asistente'
DEFAULT_TRAINING_MESSAGE = 'Se ha empezado el entrenamiento del asistente, una vez culminado se notificará vía correo electrónico.'
ERROR_MESSAGE_FLAG = ['lo siento', 'lamentablemente', '¡Hola!', 'gracias']

class AssistantHandler():
    def __init__(self, service: AssistantService):
        self.service = service

    async def train(self, data: TrainingRequest, task: BackgroundTasks):
        task.add_task(self.service.train, data)
    
        return QueryResponse(
            error=None, 
            data=QueryResponseData(answer=DEFAULT_TRAINING_MESSAGE)
        )

    async def query(self, data: QueryRequest, task: BackgroundTasks) -> QueryResponse:
        if not data.question:
            return None
        
        response = self.service.query(data, task)
        if not response:
            return QueryResponse(
                error=QueryResponseError(message=DEFAULT_MESSAGE_ERROR), 
                data=None
            )
        
        answer = response.get('answer')
        
        if data.query_mode == QueryModeEnum.qa:
            answer = self.get_response_with_reference(response)
        
        return QueryResponse(
            error=None, 
            data=QueryResponseData(answer=answer)
        )
    
    def get_response_with_reference(self, response) -> str:
        answer: str = ''
        
        if 'answer' in response and 'source_documents' in response:
            answer = response.get('answer')
            sources = response.get('source_documents')

            if len(sources) > 0:
                source = sources[0].metadata
                if 'source' in source and 'page' in source and 'url' in source:
                    if not contains(answer, ERROR_MESSAGE_FLAG):
                        reference = f"<a href='{short(source.get('url'))}'>{source.get('source')}</a> (Pag. {source.get('page')})"
                        answer = f"{answer}\n\nFuente: {reference}"

        return answer