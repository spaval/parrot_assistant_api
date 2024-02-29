# bot.py
import os
import requests
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv

DEFAULT_ERROR_MESSAGE = f'En este momento no puedo responderte, por favor inténtalo más tarde.'

bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all(),
    description="discord bot that helps with your learning about the company documentation using ai"
)

class DiscordBot:
    def __init__(self):
        env = os.getenv('env') or 'dev'
        path = f"config/.env.{env}"

        load_dotenv(path)
        
    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord!')


    @bot.event
    async def on_message(message):
        if message.author.bot or not message.content:
            return
        
        try:
            answer = query_assistant(q=message.content, chat_id=message.channel.id)
            await message.channel.send(answer)
        except Exception as e:
            await message.channel.send(DEFAULT_ERROR_MESSAGE)

    @bot.command()
    async def start(self, ctx):
        await ctx.send("You have started")
    
    def run(self):
        bot.run(os.getenv('DISCORD_TOKEN'))

def query_assistant(q: str, chat_id):
        url = f"{os.getenv('PARROT_API_BASE_URL')}/{os.getenv('PARROT_API_QUERY_PATH')}?q={q}&id={chat_id}&source=discord"
        response = requests.get(url)
        answer = DEFAULT_ERROR_MESSAGE
    
        if response.status_code == 200:
            result = response.json()
            if result and result['data']:
                data = result['data']
                answer = data['answer']

        return answer