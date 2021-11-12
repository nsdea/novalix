# CREDIT
# https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py

try:
    from .helpers import config, management
except ImportError:
    import helpers.config
    import helpers.management

import asyncio
import discord
import datetime
import humanize
import dateparser
import youtube_dl
import discord.commands

from discord.ext import commands
from discord.commands import slash_command

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


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description='🎤 Joins a voice channel.')
    async def join(
        self,
        ctx,
        channel: discord.commands.Option(
            discord.VoiceChannel, 'Channel to join (optional)', required=False, default=None)=None
    ):

        """Joins a voice channel"""
        if not channel:
            channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.respond(embed=discord.Embed(title=':white_check_mark: Joined!.', description='Now, try `/play`.', color=management.color()))

    @classmethod
    async def video_embed(ctx, player, *args, **kwargs):
        video_info = player.__dict__['data']

        embed = discord.Embed(
            title=f'{"📡" if video_info["is_live"] else "🎵"} Playing: {player.title}',
            description=f':loud_sound: Playing in {ctx.author.voice.channel.mention}',
            color=management.color(),
            timestamp=dateparser.parse(video_info['upload_date'], settings={'DATE_ORDER': 'YMD'})
        )

        embed.set_thumbnail(url=video_info['thumbnail'])
        embed.add_field(name='⌛ Duration', value=humanize.intword(datetime.timedelta(seconds=video_info['duration'])))
        embed.add_field(name='📊 Views', value=humanize.intword(video_info['view_count']))
        embed.add_field(name='👍 Likes', value=humanize.intword(video_info['like_count']))
        embed.set_author(name=video_info['uploader'], url=video_info['uploader_url'])

        return embed

    @slash_command(description='🎶 Plays a song in a voice channel.')
    async def play(
        self,
        ctx,
        search_term: discord.commands.Option(str, 'Video to play'),
    ):
        # ids = [emoji.id for emoji in ctx.guild.emojis]
        await ctx.respond(embed=discord.Embed(title='<a:NVloading:908663225736904744> Give me a moment')) # fixes misleading message <Interaction Failed>

        if not ctx.voice_client:
            return await ctx.respond(embed=discord.Embed(title=':x: You\'re not connected to a voice channel.', description='Please join a voice channel and run `/join`.', color=management.color('error')))

        player = await YTDLSource.from_url(search_term, loop=self.client.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(
            f'Player error: {e}') if e else None)

        embed = await self.video_embed(ctx=ctx, player=player)

        try:
            await ctx.respond(embed=embed)
        except:
            await ctx.send(embed=embed)

    @slash_command(description='🔊 Changes the music volume')
    async def volume(
        self,
        ctx,
        volume: discord.commands.Option(int, 'Percent', required=False, default=50),
    ):
        if ctx.voice_client is None:
            return await ctx.respond(embed=discord.Embed(title=f'Run `/join` and try again!', color=management.color('error')))

        ctx.voice_client.source.volume = volume / 100
        await ctx.respond(embed=discord.Embed(title=f'Changed volume to {volume}%.', color=management.color()))

    @slash_command(description='🛑 Stops song and disconnects from the voice channel.')
    async def stop(
        self,
        ctx,
    ):

        try:
            await ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        except:
            await ctx.respond(embed=discord.Embed(title=':x: Could not stop!', color=management.color('error')))

        else:
            await ctx.respond(embed=discord.Embed(title='🛑 Stopped', color=management.color('error')))
        
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return

        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(client):
    client.add_cog(Music(client))
