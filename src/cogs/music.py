# CREDIT
# https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py

try:
    from .helpers import config, management, voice
except ImportError:
    import helpers.config, helpers.management, helpers.voice

import discord
import datetime
import humanize
import dateparser
import discord.commands

from discord.ext import commands
from discord.commands import slash_command


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def leave(self, ctx):
        """Simulates my dad."""
        bot_account = await ctx.guild.fetch_member(self.client.user.id)
        await bot_account.move_to(None)

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

    async def video_embed(self, ctx, player, *args, **kwargs):
        video_info = player.__dict__['data']

        embed = discord.Embed(
            title=f'{"📡" if video_info["is_live"] else "🎵"} Playing: {player.title}',
            description=f'{ctx.author.voice.channel.mention}',
            color=management.color(),
            timestamp=dateparser.parse(video_info['upload_date'], settings={'DATE_ORDER': 'YMD'}),
            url=player.url,
        )

        embed.set_thumbnail(url=video_info['thumbnail'])
        embed.add_field(name='⌛ Duration', value=humanize.intword(datetime.timedelta(seconds=video_info['duration'])))
        embed.add_field(name='👍 Likes', value=humanize.intword(video_info['like_count']))
        embed.add_field(name='📊 Views', value=humanize.intword(video_info['view_count']))
        embed.set_author(name=video_info['uploader'], url=video_info['uploader_url'])
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)

        return embed

    class MusicEmbedGUI(discord.ui.View):
        def __init__(self, ctx, player):
            self.ctx = ctx
            self.player = player

            @discord.ui.button(label='Stop', style=discord.ButtonStyle.danger)
            async def button_callback(self, button, interaction, *args, **kwargs):
                await self.leave(ctx=self.ctx)

            # @discord.ui.Button(label='Download', style=discord.ButtonStyle.url, url=f'https://onlix.me/watch?v={self.player.__dict__["data"]["id"]}')
            # async def _():
            #     pass

            super().__init__()

    @slash_command(description='🎶 Plays a song in a voice channel.')
    async def play(
        self,
        ctx,
        search_term: discord.commands.Option(str, 'Video to play'),
    ):
        # ids = [emoji.id for emoji in ctx.guild.emojis]
        # await ctx.respond(embed=discord.Embed(title='<a:NVloading:908663225736904744> Give me a moment')) # fixes misleading message <Interaction Failed>
        sent = await ctx.respond(embed=discord.Embed(title='Loading...', color=management.color())) # fixes misleading message <Interaction Failed>

        await voice.ensure_voice(ctx)

        if not ctx.voice_client:
            return await ctx.respond(embed=discord.Embed(title=':x: You\'re not connected to a voice channel.', description='Please join a voice channel and run `/join`.', color=management.color('error')))

        player = await voice.play_song(client=self.client, ctx=ctx, search_term=search_term)
        embed = await self.video_embed(ctx=ctx, player=player)

        view = self.MusicEmbedGUI(ctx=ctx, player=player)
        # view.add_item(discord.ui.button(label='Go to website', url='https://example.com/', style=discord.ButtonStyle.url))
        # view = self.MusicEmbedGUI(ctx=ctx, player=player)

        await sent.edit_original_message(embed=embed, view=view)

    @slash_command(description='🔊 Changes the music volume')
    async def volume(
        self,
        ctx,
        volume: discord.commands.Option(int, 'Percent', required=False, default=1337),
    ):
        if ctx.voice_client is None:
            return await ctx.respond(embed=discord.Embed(title=f'Run `/join` and try again!', color=management.color('error')))

        if volume == 1337: # weird way to do it lol
            return await ctx.respond(embed=discord.Embed(title=f'Volume: {ctx.voice_client.source.volume * 100}%', color=management.color()))

        ctx.voice_client.source.volume = volume / 100
        await ctx.respond(embed=discord.Embed(title=f'Changed volume to {volume}%.', color=management.color()))

    @slash_command(description='⏯️ Pause or unpause a song.')
    async def pause(self, ctx):
        await ctx.guild.voice_client.pause()

    @slash_command(description='🛑 Stops song and disconnects from the voice channel.')
    async def disconnect(
        self,
        ctx,
    ):
        await self.leave(ctx=ctx)

        try:
            await ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        except:
            await ctx.respond(embed=discord.Embed(title='🛑 Stopped', color=management.color('error')))

        else:
            await ctx.respond(embed=discord.Embed(title='🛑 Stopped without any errors!', color=management.color('error')))

def setup(client):
    client.add_cog(Music(client))
