from discord import File
from discord.ext import commands
import sqlite3 as sql
import os
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter


class Graphing(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def id_to_member(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return member
        return 'User Not Found'

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

    @commands.command()
    async def top10(self, ctx):
        guild = ctx.guild.id
        author = ctx.message.author
        bar_width = 0.15

        conn = sql.connect(f'data/{guild}/stats.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, message_count FROM members")

        data = sorted(cursor.fetchall(), key=itemgetter(1))  # sorts the list of tuples by the [1] index values
        data.reverse()
        users = [await self.id_to_member(user[0], ctx) for user in data[0:10]]
        names = [user.name for user in users]
        msg_count = [user[1] for user in data[0:10]]
        conn.commit()
        conn.close()

        x_axis = np.arange(len(names))
        fig, ax = plt.subplots()
        ax.bar(x_axis, msg_count, bar_width)
        ax.set_ylabel('Message Count')
        ax.set_xmargin(5)
        ax.set_title('Top 10 Chatters')
        ax.set_xticks(x_axis)
        ax.set_xticklabels(names)
        ax.tick_params(axis='x', labelrotation=20, labelsize=9)
        ax.grid(axis='y')

        fig.savefig(f'data/{guild}/graph.png', bbox_inches='tight')

        await ctx.send(content=f'The top chatters for the {ctx.guild} server:',
                       file=File(f'data/{guild}/graph.png'))
        os.remove(f'data/{guild}/graph.png')

        if author not in users:
            await ctx.send(f"Step it up, {author.mention}, you're not even on there :smirk:")


def setup(client):
    client.add_cog(Graphing(client))
