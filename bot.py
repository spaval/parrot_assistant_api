from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler
import requests

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¿Hay algo en lo que pueda ayudarte?"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp = parrot(update.message.text)
    if resp:
        data = resp['data']

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=data['answer']
        )

def parrot(q: str):
    url = f"https://parrot-0-0-1-dev.onrender.com/parrot/query?q={q}"
    response = requests.get(url)

    if response.status_code != 200:
        return None
    
    return response.json()

if __name__ == '__main__':
    application = ApplicationBuilder().token('7089652228:AAFLlByG1cjaT8bpI4p-lDbN1tTcaqFVwOc').build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()