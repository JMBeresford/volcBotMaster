import discord
from discord.ext import commands
import sqlite3 as sql

"""This augment contains all basic moderator+ commands. Global permission system that can be
   configured client-side is planned in anticipation of user-created cogs. Server-specific
   lists of moderators are kept in the data/{server_id} directories respective to each server."""


class Moderator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mods = []
        self.mod_commands = ['purge', 'kick']
        self.mod_role = 'BotMechanic'  # Make this interchangeable

        for guild in self.client.guilds:
            with sql.connect(f'data/{guild.id}/stats.db') as conn:
                cursor = conn.cursor()

                cursor.execute('''CREATE TABLE IF NOT EXISTS commands (
                    command text PRIMARY KEY,
                    clearance text
                );
                ''')

                try:
                    for command in self.mod_commands:
                        data = (command, 'moderator')
                        cursor.execute("INSERT INTO commands(command, clearance)"
                                       "VALUES(?,?)", data)
                except sql.IntegrityError:
                    pass

        print(f'\t\tLoaded Moderator augments successfully.\n')

    async def permission(self, ctx):
        return self.mod_role in [role.name for role in ctx.author.roles]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):  # probably lots of optimization to be found here
        if self.mod_role in str(after.roles) and self.mod_role not in str(before.roles):
            with sql.connect(f'data/{after.guild.id}/stats.db') as conn:
                cursor = conn.cursor()
                data = (after.id, str(after))
                cursor.execute("INSERT INTO moderators(id, name)"
                               "VALUES(?,?)", data)
            print(f'{str(after)} has been appointed as a Moderator.')

        elif self.mod_role in str(before.roles) and self.mod_role not in str(after.roles):
            with sql.connect(f'data/{after.guild.id}/stats.db') as conn:
                cursor = conn.cursor()
                data = (after.id,)
                cursor.execute("DELETE FROM moderators WHERE id=?", data)
            print(f'{str(after)} has been removed as a Moderator.')

        else:
            pass

    @commands.command()
    async def purge(self, ctx, amount: int, target: discord.Member):
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return
        elif amount > 15:
            await ctx.send(f'I can only purge up to 15 messages back, and {amount} is more than 15.')

        def target_acquired(msg):   # replace with lambda expression in check below
            return msg.author == target

        message_murder = await ctx.message.channel.purge(limit=amount, check=target_acquired,
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
            await ctx.send(f'{ctx.author.mention}, the command "{command}" does not exist.')
            return

        with sql.connect(f'data/{ctx.guild.id}/stats.db') as conn:
            cursor = conn.cursor()
            data = (command, 'moderator')
            cursor.execute("INSERT INTO commands(command, clearance)"
                           "VAlUES(?,?)", data)

        await ctx.send(f'The command, {command}, can now only be used by {self.mod_role}s')


def setup(client):
    client.add_cog(Moderator(client))
