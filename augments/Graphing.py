from discord import File
from discord.ext import commands
import sqlite3 as sql
import os
import matplotlib.pyplot as plt


class Graphing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def serveractivity(self, ctx, *, x='week'):
        date = ctx.message.created_at
        graph_values = {}

        with sql.connect(f'data/{ctx.guild.id}/stats.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datetime FROM activity WHERE DATE(datetime)"  # querying the db for datetime objects
                           " BETWEEN DATE('now','-7 day') AND DATE('now')")

            dated_messages = [date_time for date_time in cursor]  # Sqlite returns list of tuples
            dated_messages = [date.fromisoformat(tup[0])          # thus these hoops we jump through
                              for tup in dated_messages]

        conn.close()

        for day in range(date.day-7, date.day):
            message_list = [msg for msg in dated_messages if msg.day == day]
            graph_values[day] = len(message_list)

        fig, ax = plt.subplots()
        x = list(graph_values.keys())
        y = list(graph_values.values())
        ax.plot(x, y)
        ax.set(xlabel="Day of Month", ylabel="Message Count",
               title="Server Activity")
        ax.grid()
        fig.savefig(f'data/{ctx.guild.id}/graph.png')
        await ctx.send(content="This past week's server activity:\n",
                       file=File(f'data/{ctx.guild.id}/graph.png'))
        os.remove(f'data/{ctx.guild.id}/graph.png')


def setup(client):
    client.add_cog(Graphing(client))
