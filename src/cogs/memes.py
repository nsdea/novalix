# Local
try:
    from .helpers import config, management
except ImportError:
    import helpers.config, helpers.management

import os
import random
import discord
import asyncio
import asyncpraw

from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord.commands import slash_command

load_dotenv()

class Memes(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.reddit_client = asyncpraw.Reddit(
            client_id=os.getenv('REDDIT_ID'),
            client_secret=os.getenv('REDDIT_SECRET'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent='Novalix',
            username=os.getenv('REDDIT_USERNAME'),
        )

    @slash_command(description='🔍 Search Reddit for memes')
    async def reddit(
        self, ctx,
        sub: str=discord.commands.Option(str, 'Subreddit (default: random meme sub)', required=False, default='memes|dankmemes|me_irl|wholesomememes|okbuddyretard|comedyheaven|meme'),
        randomizer: str=discord.commands.Option(int, 'Randomizer Temperature (default: 60)', required=False, default=60)
    ):
        class RedditGUI(discord.ui.View):
            @discord.ui.button(label='Another one', style=discord.ButtonStyle.primary)
            async def button_callback(self, button, interaction, *args, **kwargs):
                await send()

        async def send(ctx=ctx, sub=sub, randomizer=randomizer):
            msg = await ctx.respond(embed=discord.Embed(title='Gimme a sec...').set_footer(text='**Tip:** if it takes ages for the memes to load, set "randomizer" to a lower value (like 30), but if the memes are always the same ones, set "randomizer" to a high value.'))

            BASE_URL = 'https://reddit.com'
            
            sub_name = sub
            if '|' in sub:
                sub_name = random.choice(sub.split('|'))
            subreddit = await self.reddit_client.subreddit(sub_name)

            posts = []

            async for p in subreddit.top(random.choice(['day', 'week', 'month']), limit=randomizer):
                if random.randint(0, len(posts)) > randomizer: # to speed up
                    break

                if p.url.endswith('.jpg') and len(p.title) < 256:
                    posts.append(p)
            
            try:
                post = random.choice(posts)
            except:
                await ctx.respond(embed=discord.Embed(title='I found no post :(', description='Try another r/subreddit.', color=management.color('error')))
                return

            embed = discord.Embed(
                color=management.color(),
                url=BASE_URL + post.permalink,
                title=post.title,
                description=f'**Upvotes:** {round(post.score/1000, 1)}K ({post.upvote_ratio*100}%)',
                timestamp=datetime.fromtimestamp(post.created_utc)
            ).set_image(url=post.url).set_author(name=post.author).set_footer(text=f'r/{sub_name}')

            gui = RedditGUI()
            await ctx.respond(embed=embed, view=gui)

            return msg

        msg = await send()

def setup(client):
    client.add_cog(Memes(client))