import os
import numpy as np
import logging
from pathlib import Path    

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_previous_chat_history(self, session_id: str):
        folder = Path(os.getenv('MESSAGES_STORE_LOCATION'))
        path = os.path.join(folder, f'{session_id}.npy')

        chat_history = [] #ChatMessageHistory()
        messages = []

        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    messages = np.load(f, allow_pickle=True)
        except Exception as e:
            logger.error(f"[PARROT ERRR]: {e}")
        finally:
            if messages is not None:
                for item in messages:
                    if item['type'] == 'human':
                        #chat_history.add_user_message(item['content'])
                         pass
                    elif item['type'] == 'ai':
                        #chat_history.add_ai_message(item['content'])
                         pass

        return chat_history

def save_assistant_conversations(self, session_id: str, chat_history):
        folder = Path(os.getenv('MESSAGES_STORE_LOCATION'))
        path = os.path.join(folder, f'{session_id}.npy')
        limit = int(os.getenv('MAX_MESSAGE_LIMIT'))
        
        try:
            conversation = chat_history.dict()
            if conversation:
                messages = conversation['messages']
                messages = messages[-limit:]
                
                if not(os.path.isdir(folder)):
                    os.mkdir(folder)

                with open(path, "wb") as f:
                    np.save(f, messages, allow_pickle=True)
        except Exception as e:
            logger.error(f"[PARROT ERRR1]: {e}")