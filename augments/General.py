import json
import os
import discord
from discord.ext import commands

"""This augment contains most of the logic for obtaining user data and calculating server statistics"""


class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.message_count = {}

        for guild in self.client.guilds:
            if not os.path.exists(f'data/{guild.id}/message_count'):
                for member in guild.members:
                    self.message_count[str(member.id)] = 0

                with open(f'data/{guild.id}/message_count', 'w+') as file:
                    json.dump(self.message_count, file)

                self.message_count = {}

        print(f'\t\tLoaded General augments successfully.\n')

    async def id_to_name(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return str(member)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        with open(f'data/{ctx.guild.id}/message_count', 'r') as file:
            self.message_count = json.load(file)

        self.message_count[str(ctx.author.id)] = self.message_count[str(ctx.author.id)] + 1

        with open(f'data/{ctx.guild.id}/message_count', 'w') as file:
            json.dump(self.message_count, file)

        self.message_count = {}

    @commands.command()
    async def admins(self, ctx):
        guild = ctx.guild

        with open(f'data/{guild.id}/admins') as file:
            admins = json.load(file)
        admin_list = [member.mention for member in guild.members if member.id in admins[str(guild.id)]]
        await ctx.send(f'The admins for this server are: {admin_list}')

    @commands.command()
    async def mods(self, ctx):
        guild = ctx.guild

        with open(f'data/{guild.id}/mods', 'r') as file:
            mods = json.load(file)
        mod_list = [member.mention for member in guild.members if member.id in mods[str(guild.id)]]
        await ctx.send(f'The mods for this server are: {mod_list}')

    @commands.command()
    async def top10(self, ctx):
        guild = ctx.guild

        with open(f'data/{guild.id}/message_count') as file:
            self.message_count = json.load(file)

        message_count_sorted = sorted(self.message_count.items(), key=lambda kv: kv[1])
        message_count_sorted.reverse()

        for chatter in message_count_sorted[0:9]:
            await ctx.send(f'{await self.id_to_name(chatter[0], ctx)}: {chatter[1]}')


def setup(client):
    client.add_cog(General(client))
