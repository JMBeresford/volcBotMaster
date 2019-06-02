import json
import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def admins(self, ctx):
        guild = ctx.guild
        with open('data/admins.json') as file:
            admins = json.load(file)
        admin_list = [member.mention for member in guild.members if member.id in admins[str(guild.id)]]
        await ctx.send(f'The admins for this server are: {admin_list}')

    @commands.command()
    async def friend(self, ctx):
        try:
            await ctx.author.send_friend_request()
        except discord.Forbidden:
            await ctx.send(f'Sorry {ctx.author.mention}, I cannot send friend requests at the moment.')


def setup(client):
    client.add_cog(General(client))
