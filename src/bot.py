import music

import os
import dotenv
import socket
import discord
import asyncio
import datetime

from discord.ext import commands
from discord.app import Option
from discordTogether import DiscordTogether

dotenv.load_dotenv()  # initialize virtual environment

COLOR = 0x6e00ff
TESTING_MODE = True
PREFIX = '/'

client = commands.Bot(command_prefix='//', intents=discord.Intents.all())
togetherControl = DiscordTogether(client)

async def status_task():
    while True:
        await client.change_presence(activity=discord.Game(f'with ONLIX#1662'))
        await asyncio.sleep(10)

@client.event
async def on_ready():
    print('ONLINE as', client.user)
    client.loop.create_task(status_task())

@client.event
async def on_command_error(ctx, error):
    return
    # error: 'error message'
    error_messages = {
        commands.CheckFailure: 'There was a problem with a check.',
        commands.UserInputError: 'There was a problem with your input.',
        commands.CommandNotFound: f'Command not found. Use **`{values.prefix()}help`** for a list of commands.',
        commands.MissingRequiredArgument: f'Oops, I think you [*forgo**r*** 💀](https://i.redd.it/mc9ut2313b571.jpg) an argument, go check it using **`{values.prefix()}help {ctx.message.content.replace(values.prefix(), "").split()[0]}`**', # the f-string generates the help-command for the command
        commands.TooManyArguments: f'You gave too many arguments, use this command for help: **`{values.prefix()}help {ctx.message.content.replace(values.prefix(), "").split()[0]}`**', # the f-string generates the help-command for the command
        commands.Cooldown: 'Please be patient :)',
        # commands.MessageNotFound: 'This message could not be found.',
        # commands.ChannelNotFound: 'This channel could not be found.',
        commands.NoPrivateMessage: 'This does not work in DM channels.',
        commands.MissingPermissions: 'Sorry, you don\'t have the following permission(s) to do this:',
        commands.BotMissingPermissions: 'Sorry, I don\'t have the following permission(s) to do this:',
        commands.ExtensionError: 'This is probably a bug you can\'t do anything about, but there was a problem with an extension.',
        commands.BadArgument: f'There was a problem converting one of the argument\'s type, use this command for help: **`{values.prefix()}help {ctx.message.content.replace(values.prefix(), "").split()[0]}`**', # the f-string generates the help-command for the command
    }

    error_msg = 'Unknown error.'

    # create the error message using the dict above
    for e in error_messages.keys():
        if isinstance(error, e):
            error_msg = error_messages[e]

    # other errors:
    # - too long
    if 'Invalid Form Body' in str(error):
        error_msg = 'Sorry, I can\'t send messages that long due to Discord limitations.'

    # - bug
    if 'Command raised an exception' in str(error):
        error_msg = 'Oops, our developers maybe messed up here. This is probably a bug.'

    # add detailed info
    if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions):
        error_msg += f'\n**`{", ".join(error.missing_perms)}`**\n'

    # add full error description formatted as a code text
    error_msg += '\n\n__Error message:__\n```\n' + str(error) + '\n```'

    # create a cool embed
    embed = discord.Embed(
        title='Command Error',
        description=error_msg,
        color=0xff0000
    )
    
    # send it
    await ctx.send(embed=embed)
    if values.testing_mode() or error_msg == 'Unknown error.':
        raise error # if this is a testing system, show the full error in the console

@client.slash_command(description='Create a YouTube Together')
async def ytt(
    ctx,
):

    invite_link = await togetherControl.create_link(ctx.author.voice.channel.id, 'youtube', max_age=604800)
    await ctx.send(embed=discord.Embed(title='YouTube Together!',  description=f'> **{invite_link}**', color=discord.Color(0x0000FF)))
    
@client.slash_command()
async def commandinfo(
    ctx,
    name: Option(str, 'Ein spezifischer Befehl:')
):
    await ctx.send('Dies ist in der Beta.')
    return
    if name:
        for c in client.commands:
            if name.lower() == c.name or name.lower() in list(c.aliases):
                text = f'''
        **Information:** {c.help if c.help else ' - '}
        **Argumente:** {c.usage if c.usage else ' - '}
        **Aliasse:** {', '.join(c.aliases) if c.aliases else ' - '}
        '''
                embed = discord.Embed(
                    title='Command ' + c.name, color=COLOR, description=text)
                await ctx.send(embed=embed)
                return

        embed = discord.Embed(title='Command not found', color=COLOR,
                              description='This command does not exist...')
        await ctx.send(embed=embed)
        return

    def sortkey(x):
        return x.name

    categories = {
        '⚙️': 'Hauptsystem',
        '📃': 'Info',
        '🔧': 'Tools',
        '🔒': 'Admin-Tools',
        '🎮': 'Spiel & Spaß',
        '🔩': 'Andere'}

    # ok, somehow I managed to get this to work, don't ask me how, but it WORKS
    text = ''
    for category in categories.keys():
        text += f'\n{category} **{categories[category]}**\n'
        for command in sorted(client.commands, key=sortkey):
            if command.help.startswith(category):
                if command.aliases:
                    text += f'{command.name} *({"/".join(command.aliases)})*\n'
                else:
                    text += f'{command.name}\n'
                continue
            
    embed = discord.Embed(title='Befehle', color=COLOR, description=text)
    embed.set_footer(
        text=f'Benutze {PREFIX}help <command> für mehr Info über einen bestimmten Befehl.')
    await ctx.send(embed=embed)

# load cogs
# credit: https://youtu.be/vQw8cFfZPx0
# for filename in os.listdir(os.getcwd() + '/src/cogs/'):
#     if filename.endswith('.py'):
#         client.load_extension(f'cogs.{filename[:-3]}')

for cmd in [music.play, ]:
    client.add_application_command(cmd)

client.run(os.getenv('DISCORD_TOKEN'))  # run bot with the token set in the .env file