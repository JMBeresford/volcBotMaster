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
        data_dict = {}
        fig.suptitle('Server Activity')

        conn = sql.connect(f'/data/{ctx.guild.id}/stats.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activity WHERE datetime BETWEEN"
                       "date('now') AND date('now','-7 day)")

        date_list = [date.fromisoformat(date_time) for date_time in cursor]
        conn.commit()
        conn.close()

        for day in range(date.day-7, date.day):
            print(day)
            data_dict[day+1] = 0

        #for date_time in date_list:





def setup(client):
    client.add_cog(Graphing(client))
