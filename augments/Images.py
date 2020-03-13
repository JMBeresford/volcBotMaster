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
    async def getimage(self, ctx, index=-1):
        '''returns an image with either the given or a random index'''
        connection = psql.connect(  user = self.config['db_user'],
                                    password = self.config['db_password'],
                                    host = self.config['db_host'],
                                    port = self.config['db_port'],
                                    dbname = self.config['db_name'])

        curr = connection.cursor()

        if index == -1:
            try:
                curr.execute('''SELECT * FROM images
                                ORDER BY random()
                                LIMIT 1;''')
            except (Exception, psql.Error) as error:
                print(error)
                return

        else:
            try:
                curr.execute('''SELECT * FROM images
                                WHERE id = %s;''', (index,))
            except (Exception, psql.Error) as error:
                print(error)

        img = curr.fetchone()

        await ctx.send(content=f"Here is image#{img[0]}, posted by {img[2]}:\n {img[1]}",)



def setup(client):
    client.add_cog(Images(client))