from shared.helpers.contains import contains
from shared.url_shortener.url_shortener import short

ERROR_MESSAGE_FLAG = ['lo siento', 'lamentablemente', '¡Hola!', 'gracias']

def get_response_with_reference(response) -> str:
        answer = response.get('answer')
        
        if 'answer' in response and 'context' in response:
            answer = response.get('answer')
            sources = response.get('context')

            if len(sources) > 0:
                source = sources[0].metadata
                if 'source' in source and 'page' in source and 'url' in source:
                    if not contains(answer, ERROR_MESSAGE_FLAG):
                        reference = f"<a href='{short(source.get('url'))}'>{source.get('source')}</a> (Pag. {source.get('page')})"
                        answer = f"{answer}\n\nFuente: {reference}"

        return answer