try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import socket
import discord.commands

from discord.ext import commands
from discord.commands import slash_command, message_command

class Tools(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(send_messages=True)
    @slash_command(description='💬 Sends a message into the channel.')
    async def send(self, ctx, message: discord.commands.Option(str, 'The message text')):
        embed = discord.Embed(title=message, color=management.color())
        embed.set_footer(text=f'Sent by {ctx.author}', icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    @commands.has_permissions(add_reactions=True)
    @slash_command(description='😀 Reacts to the last message in the channel.')
    async def react(self, ctx, emoji: discord.commands.Option(str, 'The emoji to react with')):
        embed = discord.Embed(
            title='Alright!',
            description=f'I just reacted with {emoji}.',
            color=management.color(),
        )

        async for message in ctx.channel.history(limit=1):
            await message.add_reaction(emoji)
        await ctx.respond(embed=embed)

    @message_command(name='👨‍💻 Syntax highlight this message')  # creates a global message command
    async def syntax(ctx, message: discord.Message):  # message commands return the message
        await ctx.respond(f'```py\n{message.content}\n```')

def setup(client):
    client.add_cog(Tools(client))