import json
import psycopg2 as psql
import requests
import shutil
from datetime import datetime
from PIL import Image
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

            cursor.execute( '''CREATE TABLE IF NOT EXISTS
                            members(id BIGINT PRIMARY KEY,
                                    name VARCHAR(255),
                                    join_date TIMESTAMP,
                                    guilds BIGINT[]);''')

            cursor.execute( '''CREATE TABLE IF NOT EXISTS
                            messages(   id BIGSERIAL PRIMARY KEY,
                                        author_id BIGINT,
                                        author_name VARCHAR(255),
                                        sent_at TIMESTAMP,
                                        guild_id BIGINT,
                                        channel_id BIGINT,
                                        content TEXT);''')

            cursor.execute( '''CREATE TABLE IF NOT EXISTS
                            images( id BIGSERIAL PRIMARY KEY, 
                                    url VARCHAR(255) NOT NULL, 
                                    author_name VARCHAR(255), 
                                    author_id BIGINT, 
                                    guild_id BIGINT, 
                                    description TEXT[] NOT NULL DEFAULT '{}', 
                                    size BIGINT, 
                                    height INT, 
                                    width INT);''')

            for member in guild.members:
                info = (member.id, str(member).encode('utf-8'), member.joined_at, guild.id)
                try:
                    cursor.execute( '''INSERT INTO members
                                    (id,name,join_date) VALUES (%(id)s,%(name)s,%(joined)s) 
                                    ON CONFLICT ON CONSTRAINT members_pkey DO NOTHING''',
                                    {'id':info[0], 'name':info[1], 'joined':info[2]})
                    cursor.execute('''  UPDATE members SET guilds = ARRAY_APPEND(
                                        (SELECT guilds FROM members WHERE id='%(id)s'),
                                        CAST(%(guild)s as BIGINT)) WHERE id=%(id)s
                                        AND NOT
                                            (SELECT guilds FROM members WHERE id='%(id)s')
                                            @> ARRAY[CAST(%(guild)s as BIGINT)];
                                        ''', {'id': info[0], 'guild': info[3]})
                except (Exception, psql.Error) as e:
                    if e == psql.IntegrityError:
                        pass
                    print(e)
                    pass

            conn.commit()
            conn.close()

        print(f'\t\tLoaded General augments successfully.\n')

    async def id_to_name(self, member_id, ctx):
        member = self.client.get_user(member_id)
        if member == None:
            return 'User Not Found'
        else:
            return str(member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        conn = psql.connect(    user = self.config['db_user'],
                                password = self.config['db_password'],
                                host = self.config['db_host'],
                                port = self.config['db_port'],
                                dbname = self.config['db_name'])
        cursor = conn.cursor()

        info = (member.id, str(member), member.joined_at, guild.id)
            
        try:
            cursor.execute( '''INSERT INTO members (id,name,join_date) VALUES (%s,%s,%s) 
                            ON CONFLICT ON CONSTRAINT members_pkey DO NOTHING;''', (info[0],info[1],info[2]))
            cursor.execute('''  update members set guilds = array_append(
                                (select guilds from members where name='%s'),
                                cast(%s as BIGINT)) where name=%s;''', (member.id,guild.id,str(member)))
        except (Exception, psql.Error) as error:
            print(error)
            pass

        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
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

        if message.attachments != []:
            for attachment in message.attachments:
                if attachment.height != None:
                    image_info = (  attachment.url, str(message.author),
                                    message.author.id, message.guild.id,
                                    attachment.size, attachment.height,
                                    attachment.width)
                                    
                    connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

                    curr = connection.cursor()

                    try:
                        curr.execute('''INSERT INTO images
                                        (url, author_name, author_id,
                                        guild_id, size, height, width)
                                        VALUES (%s,%s,%s,%s,%s,%s,%s)''', image_info)
                    except (Exception, psql.Error) as error:
                        print(error)


        curr.close()
        connection.commit()
        connection.close()
        
    @commands.command()
    async def admins(self, ctx):
        """Lists the Administrators for the current server\n"""
        msg = f"The admins for {ctx.guild} are: \n"
        admin_role = self.config['admin_role']
        admin_list = [member for member in ctx.guild.members if admin_role in [str(role) for role in member.roles]]
        for admin in admin_list:
            msg = f"{msg}`{str(admin)}`\n"
        await ctx.send(msg)

    @commands.command()
    async def mods(self, ctx):
        """Lists the Moderators for the current server\n"""
        msg = f"The moderators for {ctx.guild} are: \n"
        mod_role = self.config['mod_role']
        mod_list = [member for member in ctx.guild.members if mod_role in [str(role) for role in member.roles]]
        for mod in mod_list:
            msg = f"{msg}`{str(mod)}`\n"
        await ctx.send(msg)



def setup(client):
    client.add_cog(General(client))
