import os
import requests
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes, MessageHandler

DEFAULT_ERROR_MESSAGE = f'En este momento no puedo responderte, por favor inténtalo más tarde.'

class TelegramBot:
    def __init__(self):
        env = os.getenv('env') or 'dev'
        path = f"config/.env.{env}"

        load_dotenv(path)

        # Enable logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"running on <<< {env} >>>")
        
    def run(self):
        application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
        start_handler = CommandHandler('start', self.start)
        help_handler = CommandHandler("help", self.help)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)

        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.add_handler(help_handler)
    
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await update.message.reply_html(
            rf"Hola <strong>{user.mention_html()}!</strong> {os.getenv('WELCOME_MESSAGE')}",
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(os.getenv('HELP_MESSAGE'))

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        answer = self.query_assistant(update.message.text, update.message.chat.id)
        await update.message.reply_html(answer)

    def query_assistant(self, q: str, chat_id):
        url = f"{os.getenv('PARROT_API_BASE_URL')}/{os.getenv('PARROT_API_QUERY_PATH')}?q={q}&id={chat_id}&source=telegram"
        response = requests.get(url)
        answer = DEFAULT_ERROR_MESSAGE
        
        if response.status_code == 200:
            result = response.json()
            if result and result['data']:
                data = result['data']
                answer = data['answer']

        return answer