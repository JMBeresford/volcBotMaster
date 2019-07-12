from discord.ext import commands
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt


class Graphing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def serveractivity(self, ctx, *, x='week'):
        date = ctx.message.created_at
        fig = plt.figure()
        fig.suptitle('Server Activity')

        with sql.connect(f'/data/{ctx.guild.id}/stats.db') as conn:
            cursor = conn.cursor()
            cursor.execute()



def setup(client):
    client.add_cog(Graphing(client))
