import sqlite3 as sql
import json
import psycopg2 as psql
from datetime import datetime
import discord
from discord.ext import commands

"""This augment contains most of the logic for obtaining user/server data"""


class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = {}
        with open('config.json') as f:
            self.config = json.load(f)

        self.message_count = {}

        for guild in self.client.guilds:
            conn = psql.connect(user = self.config['db_user'],
                                password = self.config['db_password'],
                                host = self.config['db_host'],
                                port = self.config['db_port'],
                                dbname = self.config['db_name'])

            cursor = conn.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS members(id BIGINT PRIMARY KEY, name VARCHAR(255), join_date TIMESTAMP guilds BIGINT[]);")

            cursor.execute('''CREATE TABLE IF NOT EXISTS messages(  id BIGSERIAL PRIMARY KEY,
                                                                    author_id BIGINT,
                                                                    author_name VARCHAR(255),
                                                                    sent_at TIMESTAMP,
                                                                    guild_id BIGINT,
                                                                    channel_id BIGINT,
                                                                    content TEXT);''')

            for member in guild.members:
                info = (member.id, str(member), member.joined_at, guild.id)
                try:
                    cursor.execute( 'INSERT INTO members (id,name) VALUES (%s,%s);', info[0:2])
                    cursor.execute('''  update members set guilds = array_append(
                                        (select guilds from members where name='%s'),
                                        cast(%s as BIGINT)) where name=%s;''', (member.id,guild.id,member.id))
                except (Exception, psql.IntegrityError):
                    pass


            conn.commit()
            conn.close()

        print(f'\t\tLoaded General augments successfully.\n')

    async def id_to_name(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return str(member)
        return 'User Not Found'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sql.connect(f'data/{member.guild.id}/stats.db')
        cursor = conn.cursor()

        info = (member.id, str(member), 0, member.joined_at)

        try:
            cursor.execute( '''INSERT INTO members(id, name, message_count, join_date)
                            VALUES(?,?,?,?)''', info)
            conn.commit()
        except sql.IntegrityError:
            conn.rollback()
            pass
        finally:
            conn.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            print("bot typed")
            return

        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        info = (message.author.id, str(message.author), datetime.now(),
                message.guild.id, message.channel.id, message.content)
        try:
            curr.execute('''INSERT INTO messages
                        (author_id, author_name, sent_at, guild_id, channel_id, content)
                        VALUES (%s,%s,%s,%s,%s,%s)''', info)
        except (Exception, psql.Error) as error:
            print("There was an error with the insertion:", error)
    
        curr.close()
        connection.commit()
        connection.close()
        
    @commands.command()
    async def admins(self, ctx):
        """Lists the Administrators for the current server\n"""
        guild = ctx.guild

        with sql.connect(f'data/{guild.id}/stats.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM administrators")

            data = cursor.fetchall()  # will return a list of tuples that only hold one element
            data = [admin_id[0] for admin_id in data]  # Makes a list of tuples that holds only one element just a list
            admin_list = [await self.id_to_name(admin_id, ctx) for admin_id in data]

            msg = "The admins for this server are:\n"
            for admin in admin_list:
                msg = f'{msg}{admin}\n'

            await ctx.send(msg)

        conn.close()

    @commands.command()
    async def mods(self, ctx):
        """Lists the Moderators for the current server\n"""
        guild = ctx.guild

        with sql.connect(f'data/{guild.id}/stats.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM moderators")

            data = cursor.fetchall()  # will return a list of tuples that only hold one element
            data = [mod_id[0] for mod_id in data]  # Makes a list of tuples that holds only one element just a list
            mod_list = [await self.id_to_name(mod_id, ctx) for mod_id in data]

            msg = "The mods for this server are:\n"
            for mod in mod_list:
                msg = f'{msg}{mod}\n'

            await ctx.send(msg)

        conn.close()



def setup(client):
    client.add_cog(General(client))
