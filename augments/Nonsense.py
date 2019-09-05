import discord
from discord.ext import commands

"""Self-explanatory name"""

# TODO: favoriteWord, favoriteCommand


class Nonsense(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        """Pongs your ping\n"""
        await ctx.send('Pong!')

    @commands.command()
    async def foo(self, ctx):
        """Bars your foo\n"""
        await ctx.send('Bar!')

    @commands.command()
    async def whisper(self, ctx, target: discord.Member, *, msg):
        """Have the bot whisper another user for you\n"""
        await target.send(f'{ctx.message.author} said: {msg}')

    @commands.command()
    async def penis(self, ctx, target: discord.Member):
        """The bot physically measures your length\n"""
        if target.id == 174439608577294336:
            await ctx.send(f"{target.mention}'s length: 8{'=' * 31}D")
        else:
            length = target.id % 30
            await ctx.send(f"{target.mention}'s length: 8{'=' * length}D")


def setup(client):
    client.add_cog(Nonsense(client))
