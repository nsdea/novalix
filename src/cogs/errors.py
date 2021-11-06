try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import discord

from discord.ext import commands
from discord.commands import slash_command

class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        embed = discord.Embed(
            title='Command Error',
            description=f'```py\n{str(error)}```',
            color=management.color('error')
        )
        
        try:
            await ctx.respond(embed=embed)
        except:
            await ctx.send(embed=embed)

        if management.testing_mode():
            raise error # if this is a testing system, show the full error in the console

def setup(client):
    client.add_cog(Errors(client))