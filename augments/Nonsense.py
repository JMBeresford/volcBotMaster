import discord
from discord.ext import commands

"""Self-explanatory name"""

# TODO: favoriteWord, favoriteCommand


class Nonsense(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def foo(self, ctx):
        await ctx.send('Bar!')

    @commands.command()
    async def whisper(self, ctx, target: discord.Member, *, msg):
        await target.send(f'{ctx.message.author} said: {msg}')

    @commands.command()
    async def penis(self, ctx, target: discord.Member):
        length = target.id % 30
        await ctx.send(f"{target.mention}'s length: 8{'=' * length}D")


def setup(client):
    client.add_cog(Nonsense(client))
