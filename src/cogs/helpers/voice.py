from . import management

import discord
import asyncio
import youtube_dl

from discord.ext import commands

# Suppress noiseout console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def play_song(client, ctx, search_term: str):
    global ytdl

    if isinstance(ctx, commands.Context):
        voice_system = ctx.voice_client
    else:
        voice_system = ctx.guild.voice_client

    player = await YTDLSource.from_url(search_term, loop=client.loop, stream=True)
    try:
        voice_system.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
    except discord.errors.ClientException:
        return await ctx.respond(embed=discord.Embed(title=':x: You\'re not connected to a voice channel.', description='Please join a voice channel and run `/join`.', color=management.color('error')))

    ytdl.cache.remove()
    return player

async def ensure_voice(ctx):
    if isinstance(ctx, commands.Context):
        voice_system = ctx.voice_client
    else:
        voice_system = ctx.guild.voice_client

    if voice_system is None:
        try:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return
        except AttributeError:
            pass

    elif voice_system.is_playing():
        voice_system.stop()
