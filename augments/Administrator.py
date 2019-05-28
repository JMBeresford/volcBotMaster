import discord
from discord.ext import commands


class Administrator(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ban(self, ctx, target: discord.Member, *, because='because reasons'):
        await target.ban(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')


def setup(client):
    client.add_cog(Administrator(client))
