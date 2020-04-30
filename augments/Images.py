import discord
import json
import psycopg2 as psql
from discord.ext import commands

"""
This augment is for the displaying and manipulation
of the images stored by the bot from user messages.
"""

class Images(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = {}
        with open('config.json') as f:
            self.config = json.load(f)
        
        print(f'\t\tLoaded Images augments successfully.\n')

    @commands.command()
    async def getimage(self, ctx, index=0):
        '''returns an image with either the given or a random index'''
        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        if index == 0:
            try:
                curr.execute('''SELECT * FROM images
                                WHERE guild_id = %(guild_id)s
                                ORDER BY random()
                                LIMIT 1;''', {'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)
                return

        elif index < 0:
            try:
                curr.execute('''SELECT * FROM images
                                WHERE id = ((SELECT count(*)
                                FROM images) + %(index)s + 1)
                                AND guild_id = %(guild_id)s;''', {'index': index, 'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)

        else:
            try:
                curr.execute('''SELECT * FROM images
                                WHERE id = %(index)s
                                AND guild_id = %(guild_id)s;''', {'index': index, 'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)

        img = curr.fetchone()

        if img == None:
            await ctx.send(f"That image does not exist.")

        if img[4] != ctx.guild.id:
            await ctx.send(f"That image is not of this world...")
            return

        await ctx.send(content=f"Here is image#{img[0]}, posted by {img[2]}:\n {img[1]}",)


    @commands.command()
    async def countimagesfrom(self,ctx,target: discord.Member):
        target_id = target.id

        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        try:
            curr.execute('''SELECT count(*) FROM images
                            WHERE author_id = %s;''', (target_id,))
        except (Exception, psql.Error) as error:
            print(error)

        count = curr.fetchone()[0]

        await ctx.send(f"`{str(target)}` has sent `{count}` images/videos.")


    @commands.command()
    async def countimages(self,ctx):
        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        try:
            curr.execute('''SELECT count(*) FROM images
                            WHERE guild_id = %s;''', (ctx.guild.id,))
        except (Exception, psql.Error) as error:
            print(error)

        count = curr.fetchone()

        count = (count[0] if count != None else 0)

        await ctx.send(f"I have `{count}` images/videos stored from this server.")


    @commands.command()
    async def describeimage(self,ctx,index=0, *, words=""):
        if index <= 0:
            await ctx.send(f"Please enter a proper image index.")

        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        words = [word for word in words.split()]

        try:
            curr.execute('''UPDATE images SET description = (
                            description || '%(words)s'
                            ) WHERE id=%(idx)s;''',
                            {'idx': index, 'words': words})
        except Exception as error:
            print(error)

        try:
            curr.execute('''SELECT description FROM images
                            WHERE id = %s;''', [index])
        except (Exception, psql.Error) as error:
            print(error)

        await ctx.send(f"Description for image#{index} is now {curr.fetchone()}")

def setup(client):
    client.add_cog(Images(client))