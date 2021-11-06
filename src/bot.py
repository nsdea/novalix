# IMPORTS

from cogs.helpers import config, management

import os
import dotenv
import discord
import asyncio
import discord.commands

from discord.ext import commands
from discord_together import DiscordTogether

# SETTINGS
COLOR = config.load()['color-primary']
TESTING_MODE = management.testing_mode()
PREFIX = '//'

# SETUP
dotenv.load_dotenv()  # initialize virtual environment
token = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

async def status_task():
    while True:
        await client.change_presence(activity=discord.Game(f'in BETA'))
        await asyncio.sleep(10)

@client.event
async def on_ready():
    print('ONLINE as', client.user)

    client.togetherControl = await DiscordTogether(token)
    client.loop.create_task(status_task())
    
# load cogs
# credit: https://youtu.be/vQw8cFfZPx0
for filename in os.listdir(os.getcwd() + '/src/cogs/'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)  # run bot with the token set in the .env file