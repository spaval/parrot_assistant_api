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
        bad_command_handler = CommandHandler("bad_command", self.bad_command)
        

        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)

        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.add_handler(help_handler)
        application.add_handler(bad_command_handler)
        application.add_error_handler(self.error)
    
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

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        self.logger.error("Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # Finally, send the message
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )

    async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.wrong_method_name()

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        resp = self.query_assistant(update.message.text)
        if resp:
            data = resp['data']
            await update.message.reply_text(data['answer'])

    def query_assistant(self, q: str):
        url = f"{os.getenv('PARROT_API_BASE_URL')}/{os.getenv('PARROT_API_QUERY_PATH')}?q={q}"
        response = requests.get(url)

        if response.status_code != 200:
            return None
        
        return response.json()