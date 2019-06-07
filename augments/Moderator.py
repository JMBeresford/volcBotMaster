import discord
from discord.ext import commands
import json
import os

"""This augment contains all basic moderator+ commands. Global permission system that can be
   configured client-side is planned in anticipation of user-created cogs. Server-specific
   lists of moderators are kept in the data/{server_id} directories respective to each server."""


class Moderator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mods = []
        self.mod_commands = []
        self.mod_role = 'BotMechanic'  # Make this interchangeable

        for guild in self.client.guilds:
            self.mods = [member.id for member in guild.members
                         if self.mod_role in str(member.roles)]

            with open(f'data/{guild.id}/mods', 'w+') as file:
                json.dump(self.mods, file)

            if os.path.exists(f'data/{guild.id}/mod_commands'):
                pass
            else:
                self.mod_commands = ['purge', 'kick', 'restrict']
                with open(f'data/{guild.id}/mod_commands', 'w+') as file:
                    json.dump(self.mod_commands, file)

                self.mod_commands = []

        print(f'\t\tLoaded Moderator augments successfully.\n')

    async def permission(self, ctx):
        return self.mod_role in [role.name for role in ctx.author.roles]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):  # probably lots of optimization to be found here
        if self.mod_role in str(after.roles) and self.mod_role not in str(before.roles):
            self.mods = [member.id for member in after.guild.members
                         if self.mod_role in str(member.roles)]
            print(f'{str(after)} has been appointed as a Moderator.')
            with open(f'data/{after.guild.id}/mods', 'w') as file:
                json.dump(self.mods, file)

        elif self.mod_role in str(before.roles) and self.mod_role not in str(after.roles):
            self.mods = [member.id for member in after.guild.members
                         if self.mod_role in str(member.roles)]
            print(f'{str(after)} has been removed as a Moderator.')
            with open(f'data/{after.guild.id}/mods', 'w') as file:
                json.dump(self.mods, file)

        else:
            pass

    @commands.command()
    async def purge(self, ctx, amount, target: discord.Member):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        def target_acquired(msg):   # replace with lambda expression in check below
            return msg.author == target

        message_murder = await ctx.message.channel.purge(limit=int(amount), check=target_acquired,
                                                         before=ctx.message)

        await ctx.send(f"Purged {len(message_murder)} of {target.mention}'s messages.")

    @commands.command()
    async def kick(self, ctx, target: discord.Member, *, because='because reasons'):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        await target.kick(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')

    @commands.command()
    async def restrict(self, ctx, command: str):
        if self.client.get_command(command) is None:
            await ctx.send(f'{ctx.author.mention}, the command ```{command}``` does not exist.')
            return

        with open(f'data/{ctx.guild.id}/mod_commands', 'a') as file:
            self.mod_commands = [command]
            json.dump(self.mod_commands, file)
            self.mod_commands = []

        await ctx.send(f'The command, {command}, can now only be used by {self.mod_role}s')


def setup(client):
    client.add_cog(Moderator(client))
