import discord
from discord.ext import commands


class Moderator(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def purge(self, ctx, amount, target: discord.Member):
        def target_acquired(msg):
            return True if msg.author == target else False

        message_murder = await ctx.message.channel.purge(limit=amount, check=target_acquired, before=ctx.message)

        await ctx.send(f"Purged {len(message_murder)} of {target.name}'s messages.")

    @commands.command()
    async def kick(self, ctx, target: discord.Member, *, because='because reasons'):
        await target.kick(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')


def setup(client):
    client.add_cog(Moderator(client))
