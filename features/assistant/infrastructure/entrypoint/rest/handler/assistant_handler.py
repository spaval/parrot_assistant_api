from features.assistant.application.assistance_service import AssistantService
from features.assistant.infrastructure.entrypoint.rest.handler.dto.training import Training
from shared.helpers.contains import contains
from shared.url_shortener.url_shortener import short

from fastapi import BackgroundTasks

DEFAULT_MESSAGE_ERROR = 'No se pudo obtener una respuesta por parte del asistente'
DEFAULT_TRAINING_MESSAGE = 'Se ha empezado el entrenamiento del asistente, una vez culminado se notificará vía correo electrónico.'
ERROR_MESSAGE_FLAG = ['lo siento', 'lamentablemente', '¡Hola!', 'gracias', 'no cuentas con la información', 'no puedo']

class AssistantHandler():
    def __init__(self, service: AssistantService):
        self.service = service

    async def train(self, data: Training, task: BackgroundTasks):
        task.add_task(self.service.train, data.email)
            
        return {
            "error": None,
            "data": {
                "answer": DEFAULT_TRAINING_MESSAGE
            }
        }

    async def query(self, q, id, source, task: BackgroundTasks):
        if q is None:
            return None
        
        error: str = DEFAULT_MESSAGE_ERROR
        answer: str = ''
        source: str = ''
        
        response = self.service.query(q, id, source, task)
        if response:
            error = None
            answer = response.get('answer')
            sources = response.get('source_documents')

            if sources:
                source = sources[0].metadata
                if source.get('source') and source.get('page') and source.get('url'):
                    if not contains(answer, ERROR_MESSAGE_FLAG):
                        reference = f"<a href='{short(source.get('url'))}'>{source.get('source')}</a> (Pag. {source.get('page')})"
                        answer = f"{answer}\n\nFuente: {reference}"
        
        return {
            "error": error,
            "data": {
                "answer": answer,
            }
        }