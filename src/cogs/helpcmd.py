try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import discord.commands

from discord.ext import commands
from discord.commands import slash_command

class HelpCmd(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(aliases=['help'])
    async def info(self, ctx):
        embed = discord.Embed(title='Help', color=management.color(), description='I\'m to lazy for this right now, enjoy this meme instead--')
        embed.set_image('https://sayingimages.com/wp-content/uploads/stop-it-help-meme.jpg')
        await ctx.respond(embed=embed)

def setup(client):
    client.add_cog(HelpCmd(client))