import discord
import json
from discord.ext import commands

"""
This augment contains all basic administrator commands. Global permission system that can be
configured client-side is planned in anticipation of user-created cogs. Server-specific
lists of administrators are kept in the data/{server_id} directories respective to each server.
"""


class Administrator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = {}
        with open('config.json') as f:
            self.config = json.load(f)
        self.admin_commands = ['ban', 'die', 'mod']
        self.admin_role = self.config['admin_role']

        print(f'\t\tLoaded Administrator augments successfully.\n')

    async def permission(self, ctx):
        return self.admin_role in [role.name for role in ctx.author.roles]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.admin_role in str(after.roles) and self.admin_role not in str(before.roles):
            print(f'{str(after)} has been appointed as a Administrator.')

        elif self.admin_role in str(before.roles) and self.admin_role not in str(after.roles):
            print(f'{str(after)} has been removed as a Administrator.')

        else:
            pass

    @commands.command()
    async def ban(self, ctx, target: discord.Member, *, because='because reasons'):
        """Bans target user\n"""
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        await target.ban(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')


def setup(client):
    client.add_cog(Administrator(client))
