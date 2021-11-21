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

import difflib
import discord

from discord.ext import commands

class CraftChat(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'unique players ever joined' in message.channel.topic: # channel is a DiscordSRV webhook chatsync channel
            if '!play ' in message.content:
                await voice.ensure_voice(message)

                try:
                    player = await voice.play_song(client=self.client, ctx=message, search_term=message.content.split('!play ')[1])
                except AttributeError:
                    await message.channel.send(f'[NOVALIX CraftChat] Please do !join @user or #channel first, for example: "!join #music" or "!join @ONLIX"')
                else:
                    await message.channel.send(f'[NOVALIX CraftChat] Playing Song: {player.title}')

            if '!join ' in message.content:
                selected = message.content.split('!join ')[1]
                is_channel = selected[0] == '#'

                if is_channel:
                    channel_names = [c.name for c in message.guild.voice_channels]
                    found = difflib.get_close_matches(word=selected[1:], possibilities=channel_names, n=1)[0] # I could leave this out, but it's for the UX
                    channel = discord.utils.get(message.guild.voice_channels, name=found)
                    
                else:
                    member_names = [m.name for m in message.guild.members]
                    found = difflib.get_close_matches(word=selected[1:], possibilities=member_names, n=1)[0] # I could leave this out, but it's for the UX
                    member = discord.utils.get(message.guild.members, name=found)
                    channel = member.voice.channel
            
                await channel.connect()
                await message.channel.send(f'[NOVALIX CraftChat] Joined #{channel.name}!')


def setup(client):
    client.add_cog(CraftChat(client))