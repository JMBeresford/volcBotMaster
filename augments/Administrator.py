import discord
import sqlite3 as sql
from discord.ext import commands

"""
This augment contains all basic administrator commands. Global permission system that can be
configured client-side is planned in anticipation of user-created cogs. Server-specific
lists of administrators are kept in the data/{server_id} directories respective to each server.
"""


class Administrator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.admin_commands = ['ban', 'die', 'mod']
        self.admin_role = 'BotOfficer'  # Make this interchangeable

        for guild in self.client.guilds:
            with sql.connect(f'data/{guild.id}/stats.db') as conn:
                cursor = conn.cursor()

                cursor.execute( '''CREATE TABLE IF NOT EXISTS commands (
                                command text PRIMARY KEY,
                                clearance text);''')

                try:
                    for command in self.admin_commands:
                        data = (command, 'administrator')
                        cursor.execute( "INSERT INTO commands(command, clearance)"
                                        "VALUES(?,?)", data)
                except sql.IntegrityError:
                    pass

            conn.close()

        print(f'\t\tLoaded Administrator augments successfully.\n')

    async def permission(self, ctx):
        return self.admin_role in [role.name for role in ctx.author.roles]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.admin_role in str(after.roles) and self.admin_role not in str(before.roles):
            with sql.connect(f'data/{after.guild.id}/stats.db') as conn:
                cursor = conn.cursor()
                data = (after.id, str(after))
                cursor.execute( "INSERT INTO administrators(id, name)"
                                "VALUES(?,?)", data)
            conn.close()
            print(f'{str(after)} has been appointed as a Administrator.')

        elif self.admin_role in str(before.roles) and self.admin_role not in str(after.roles):
            with sql.connect(f'data/{after.guild.id}/stats.db') as conn:
                cursor = conn.cursor()
                data = (after.id,)
                cursor.execute("DELETE FROM administrators WHERE id=?", data)

            conn.close()
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

    @commands.command()
    async def mod(self, ctx, target: discord.Member):  # TODO: fix
        """Grants target user Mod privileges\n"""
        if not await self.permission(ctx):
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')
            return

        for role in ctx.guild.roles:
            if str(role) is "BotMechanic":
                await target.add_roles(role.id, reason=None, atomic=True)
                await ctx.send(f'{target.mention} has been modded!')
                break


def setup(client):
    client.add_cog(Administrator(client))
