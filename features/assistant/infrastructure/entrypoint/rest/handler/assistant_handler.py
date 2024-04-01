from dotenv import load_dotenv
from fastapi import BackgroundTasks
from features.assistant.application.assistance_service import AssistantService
from features.assistant.infrastructure.entrypoint.rest.handler.dto.query import QueryResponse, QueryResponseData, QueryResponseError
from features.assistant.infrastructure.entrypoint.rest.handler.dto.training import TrainingRequest
from features.assistant.infrastructure.entrypoint.rest.handler.dto.query import QueryRequest, QueryShoppingRequest
from features.assistant.infrastructure.helpers.get_source import get_response_with_reference

DEFAULT_MESSAGE_ERROR = 'No se pudo obtener una respuesta por parte del asistente'
DEFAULT_TRAINING_MESSAGE = 'Se ha empezado el entrenamiento del asistente, una vez culminado se notificará vía correo electrónico.'

class AssistantHandler():
    def __init__(self, service: AssistantService):
        self.service = service

    async def on_startup(self) -> None:
        print('Aplication started!')

    async def train(self, data: TrainingRequest, task: BackgroundTasks):
        task.add_task(self.service.train, data)
    
        return QueryResponse(
            error=None, 
            data=QueryResponseData(answer=DEFAULT_TRAINING_MESSAGE)
        )

    async def query(self, data: QueryRequest, task: BackgroundTasks) -> QueryResponse:
        try:
            data = data.dict()
            response = await self.service.query(data, task)
            answer = get_response_with_reference(response)
            
            return QueryResponse(
                error=None, 
                data=QueryResponseData(answer=answer)
            )
        except Exception as e:
            return QueryResponse(
                error=QueryResponseError(
                    code=500,
                    message=str(e),
                ),
                data=None,
            )
    
    async def shop(self, data: QueryShoppingRequest, task: BackgroundTasks) -> QueryResponse:
        try:
            data = data.dict()
            response = await self.service.shop(data, task)

            return QueryResponse(
                error=None,
                data=QueryResponseData(
                    answer=response.get('answer'),
                )
            )
        except Exception as e:
            return QueryResponse(
                error=QueryResponseError(
                    code=500,
                    message=str(e),
                ),
                data=None,
            )
    