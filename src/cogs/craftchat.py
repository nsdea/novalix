"""
WARNING: This extension is EXTREMELY UNSTABLE and not recommended for general usage.
This is mainly for my own servers.

The reason why this system isn't recommended to actually use in production is that
message content scopes will get massive restrictions soon (March 2022).
From then, all systems/extensions that use message.content/on_message won't work
perfectly fine anymore, especially if your bot reaches 100 serves and still isn't
verified. It's too complicated to write down here though.  

====================================================================================

Install DiscordSRV (or a similar plugin with specific settings, but you should use DiscordSRV
as there are some things that work best with it) to your Minecraft server to use this!

Which CraftChat, you can use some features, like music, while in your Minecraft server. You can use (some)
commands and more! (Very unstable though!!!)
"""

try:
    from .helpers import config, management, voice
except ImportError:
    import helpers.config, helpers.management, helpers.voice

import discord

from discord.ext import commands

class CraftChat(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if '!play ' in message.content and 'unique players ever joined' in message.channel.topic:
            await voice.ensure_voice(message)

            player = await voice.play_song(client=self.client, ctx=message, search_term=message.content.split('!play ')[1])
            await message.channel.send(f'[NOVALIX CraftChat] Playing Song: {player.title}')

def setup(client):
    client.add_cog(CraftChat(client))