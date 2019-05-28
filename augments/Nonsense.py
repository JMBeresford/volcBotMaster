import discord
from discord.ext import commands


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


def setup(client):
    client.add_cog(Nonsense(client))
