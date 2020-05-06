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
        '''Returns an image with either the given, or a random index'''
        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        if index == 0:
            try:
                curr.execute('''SELECT ROW_NUMBER() OVER(ORDER BY id) id, url, author_name
                                FROM images
                                WHERE guild_id = %(guild_id)s
                                ORDER BY random()
                                LIMIT 1;''', {'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)
                return

        elif index < 0:
            try:
                curr.execute('''SELECT id, url, author_name
                                FROM (
                                    SELECT ROW_NUMBER() OVER(ORDER BY id) id, url, author_name
                                    FROM images
                                    WHERE guild_id = %(guild_id)s
                                    ORDER BY id DESC
                                    LIMIT (-1 *%(index)s)
                                ) AS reversed_guild_subset
                                ORDER BY id ASC
                                ''', {'index': index, 'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)

        else:
            try:
                curr.execute('''SELECT id,url,author_name FROM (
                                    SELECT ROW_NUMBER() OVER(ORDER BY id) id, url, author_name
                                    FROM images
                                    WHERE guild_id = %(guild_id)s
                                ) AS guild_subset
                                WHERE id = %(index)s
                                ''', {'index': index, 'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)

        img = curr.fetchone()

        if img == None:
            await ctx.send(f"That image does not exist.")

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
        changed = False
        if index <= 0:
            await ctx.send(f"Please enter a proper image index.")

        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        words = [word for word in words.split()]

        if words != []:
            try:
                curr.execute('''UPDATE images SET description = (
                                description || %(words)s)
                                WHERE id=(
                                    SELECT id
                                    FROM (
                                        SELECT ROW_NUMBER() OVER(ORDER BY id) id_sub, id
                                        FROM images
                                        WHERE guild_id = %(guild_id)s
                                    ) AS guild_subset
                                    WHERE id_sub = %(idx)s
                                );''',
                                {'idx': index, 'words': words, 'guild_id': ctx.guild.id})
            except (Exception, psql.Error) as error:
                print(error)
            finally:
                connection.commit()
                changed = True

        try:
            curr.execute('''SELECT description FROM (
                                SELECT ROW_NUMBER() OVER(ORDER BY id) id_sub, description
                                FROM images
                                WHERE guild_id = %(guild_id)s
                            ) AS guild_subset
                            WHERE id_sub = %(id)s;''', {'id':index, 'guild_id':ctx.guild.id})
        except (Exception, psql.Error) as error:
            print(error)

        if changed:
            await ctx.send(f"Description for image#{index} is now {', '.join(curr.fetchone()[0])}")
        else:
            await ctx.send(f"Image {index} is: {', '.join(curr.fetchone()[0])}.")


def setup(client):
    client.add_cog(Images(client))