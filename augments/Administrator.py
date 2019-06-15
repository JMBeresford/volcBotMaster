import discord
from discord.ext import commands
import json

"""This augment contains all basic administrator+ commands. Global permission system that can be
   configured client-side is planned in anticipation of user-created cogs. Server-specific
   lists of administrators are kept in the data/{server_id} directories respective to each server."""


class Administrator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.admins = []
        self.admin_role = 'BotOfficer'  # Make this interchangeable

        for guild in self.client.guilds:
            self.admins = [member.id for member in guild.members
                           if self.admin_role in str(member.roles)]

            with open(f'data/{guild.id}/admins', 'w+') as file:
                json.dump(self.admins, file)

        print(f'\t\tLoaded Administrator augments successfully.\n')

    async def permission(self, ctx):
        return self.admin_role in [role.name for role in ctx.author.roles]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.admin_role in str(after.roles) and self.admin_role not in str(before.roles):
            self.admins = [member.id for member in after.guild.members
                           if self.admin_role in str(member.roles)]
            print(f'{str(after)} has been appointed as an Administrator.')
            with open(f'data/{after.guild.id}/admins', 'w') as file:
                json.dump(self.admins, file)

        elif self.admin_role in str(before.roles) and self.admin_role not in str(after.roles):
            self.admins = [member.id for member in after.guild.members
                           if self.admin_role in str(member.roles)]
            print(f'{str(after)} has been removed as an Administrator.')
            with open(f'data/{after.guild.id}/admins', 'w') as file:
                json.dump(self.admins, file)

        else:
            pass

    @commands.command()
    async def ban(self, ctx, target: discord.Member, *, because='because reasons'):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        await target.ban(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')

    @commands.command()
    async def die(self, ctx):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        await ctx.send('Shutting down... :wave:')
        await self.client.close()

    @commands.command()
    async def mod(self, ctx, target: discord.Member):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        for role in ctx.guild.roles:
            if str(role) is "BotMechanic":
                mod_role_literal = role
                await target.add_roles(mod_role_literal, reason=None, atomic=True)
                await ctx.send(f'{ctx.author.mention} has been modded!')
                break


def setup(client):
    client.add_cog(Administrator(client))
