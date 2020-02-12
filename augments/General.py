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

            cursor.execute("CREATE TABLE IF NOT EXISTS members(id BIGINT PRIMARY KEY, name VARCHAR(255), join_date TIMESTAMP, guilds BIGINT[]);")

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
                    cursor.execute( 'BEGIN '
                                        'IF NOT EXISTS (SELECT * FROM members WHERE id = %(id)s)'
                                        'BEGIN '
                                            'INSERT INTO members (id,name,join_date) VALUES (%(id)s,%(name)s,%(joined)s)'
                                        'END'
                                    'END', {'id':info[0], 'name':info[1], 'joined':info[2]})
                    cursor.execute('''  update members set guilds = array_append(
                                        (select guilds from members where id='%(id)s'),
                                        cast(%(guild)s as BIGINT)) where id=%(id)s;''', {'id': info[0], 'guild': info[3]})
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
            cursor.execute( 'INSERT INTO members (id,name, join_date) VALUES (%s,%s,%s);', info[0:3])
            cursor.execute('''  update members set guilds = array_append(
                                (select guilds from members where name='%s'),
                                cast(%s as BIGINT)) where name=%s;''', (member.id,guild.id,member.id))
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
