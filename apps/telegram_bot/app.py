import os
import requests
import html
import json
import logging
import traceback

from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.constants import ParseMode
from telegram.ext import filters, Application, CommandHandler, ContextTypes, MessageHandler

DEVELOPER_CHAT_ID = 123456789

class TelegramBot:
    def __init__(self):
        load_dotenv("config/.env")

        # Enable logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)
        
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
            rf"Hi {user.mention_html()}! ¿Hay algo en lo que pueda ayudarte?",
            reply_markup=ForceReply(selective=True),
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Veci te ayuda a conocer todo sobre tu Unidad Residencial Origen")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        resp = self.query_assistant(update.message.text)
        if resp:
            data = resp['data']
            await update.message.reply_text(data['answer'])

    def query_assistant(self, q: str):
        url = f"{os.getenv('PARROT_API_BASE_URL')}/{os.getenv('PARROT_API_QUERY_PATH')}?q={q}"
        response = requests.get(url)

        if response.status_code != 200:
            return {
                "data": {
                    "answer": response.text
                }
            }
        
        return response.json()