import json
import sqlite3 as sql
import os
import discord
from discord.ext import commands

"""This augment contains most of the logic for obtaining user/server data"""


class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.message_count = {}

        for guild in self.client.guilds:
            mods = [member for member in guild.members if 'BotMechanic' in [role.name for role in member.roles]]
            admins = [member for member in guild.members if 'BotOfficer' in [role.name for role in member.roles]]
            conn = sql.connect(f'data/{guild.id}/users.db')
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id integer PRIMARY KEY,
                    name text,
                    message_count integer,
                    join_date text
            );
            ''')

            for member in guild.members:
                info = (member.id, str(member), 0, member.joined_at)
                try:
                    cursor.execute('''INSERT INTO members(id, name, message_count, join_date)
                                   VALUES(?,?,?,?)''', info)
                except sql.IntegrityError:
                    pass

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderators (
                    id integer PRIMARY KEY,
                    name text
            );
            ''')

            for mod in mods:
                info = (mod.id, mod.name)
                try:
                    cursor.execute('''INSERT INTO moderators(id, name)
                                                   VALUES(?,?)''', info)
                except sql.IntegrityError:
                    pass

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS administrators (
                    id integer PRIMARY KEY,
                    name text
            );
            ''')

            for admin in admins:
                info = (admin.id, admin.name)
                try:
                    cursor.execute('''INSERT INTO administrators(id, name)
                                   VALUES(?,?)''', info)
                except sql.IntegrityError:
                    pass

            conn.commit()
            conn.close()

        print(f'\t\tLoaded General augments successfully.\n')

    async def id_to_name(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return str(member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sql.connect(f'data/{member.guild.id}/users.db')
        cursor = conn.cursor()

        info = (member.id, str(member), 0, member.joined_at)

        try:
            cursor.execute('''INSERT INTO members(id, name, message_count, join_date)
                           VALUES(?,?,?,?)''', info)
            conn.commit()
        except sql.IntegrityError:
            conn.rollback()
            pass
        finally:
            conn.close()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        conn = sql.connect(f'data/{ctx.guild.id}/users.db')
        cursor = conn.cursor()

        info = (ctx.author.id,)

        cursor.execute("SELECT message_count, id FROM members WHERE id=?", info)
        data = cursor.fetchone()

        data = (data[0]+1, data[1])

        cursor.execute("UPDATE members SET message_count=? WHERE id=?", data)

        conn.commit()
        conn.close()

    @commands.command()
    async def admins(self, ctx):
        guild = ctx.guild
        conn = sql.connect(f'data/{guild.id}/users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM administrators")
        data = cursor.fetchall()  # will return a list of tuples that only hold one element
        data = [admin_id[0] for admin_id in data]  # Makes a list of tuples that holds only one element just a list
        admin_list = [await self.id_to_name(admin_id, ctx) for admin_id in data]

        conn.close()

        msg = "The admins for this server are:\n"
        for admin in admin_list:
            msg = f'{msg}{admin}\n'

        await ctx.send(msg)

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
