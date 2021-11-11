try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import discord

from discord.ext import commands
from discord.commands import slash_command

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description='📺 Create a YouTube Together')
    async def ytt(self, ctx, channel: discord.VoiceChannel=None):
        if not channel: # no channel is specified
            if ctx.author.voice: # user is in a voice channel
                channel = ctx.author.voice.channel # use the user's current voice channel
            else:
                return await ctx.respond(embed=discord.Embed(title='YouTube Together!',  description=f'Join a voice channel and try again!', color=management.color('error')))

        invite_link = await self.client.togetherControl.create_link(channel.id, 'youtube')
        await ctx.respond(embed=discord.Embed(title='YouTube Together!',  description=f'Click here: **{invite_link}**', color=management.color()))

def setup(client):
    client.add_cog(Fun(client))