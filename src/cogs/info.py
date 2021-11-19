try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import socket
import discord.commands

from discord.ext import commands
from discord.commands import slash_command

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(name='help', aliases=['info'], description='📃 General Bot Information')
    async def info(self, ctx):
        embed = discord.Embed(title='Help', color=management.color(), description='I\'m to lazy for this right now, enjoy this meme instead--')
        embed.set_image(url='https://sayingimages.com/wp-content/uploads/stop-it-help-meme.jpg')
        
        await ctx.respond(embed=embed)

    @slash_command(description='📊 Lists this bot\'s statistics.')
    async def stats(self, ctx):
        embed = discord.Embed(
            title='Bot Stats',
            description='Here are some stats for this instance of NOVALIX:',
            color=management.color(),
        )
        embed.add_field(name='Servers', value=f'{len(self.client.guilds)}')
        embed.add_field(name='Members', value=f'{len(self.client.users)}')
        embed.set_footer(text='Thank you everyone! 💙')
        
        await ctx.respond(embed=embed)

    @slash_command(description='📡 Connection statistics')
    async def ping(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        embed = discord.Embed(title='Statistics', color=management.color(), timestamp=management.get_start_time())
        embed.add_field(name=':desktop: Ping', value=str(round(self.client.latency * 1000, 2)) + 'ms')
        
        try:
            embed.add_field(name=':loud_sound: Voice client', value=str(round(voice.latency * 1000, 2)) + 'ms')
        except:
            embed.add_field(name=':loud_sound: Voice client', value='*[inactive]*')
        
        embed.add_field(name=f':gear: Hosted on', value=f'{socket.gethostname()}', inline=False)
        embed.set_footer(text='Bot started at: ')

        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Info(client))