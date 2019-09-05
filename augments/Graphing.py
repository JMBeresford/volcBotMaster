from discord import File
from discord.ext import commands
import sqlite3 as sql
import os
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
from datetime import datetime

"""The logic for graphing is all implemented here"""


class Graphing(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def id_to_member(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return member
        return 'User Not Found'

    @commands.command()
    async def serveractivity(self, ctx, *, time='week'):  # TODO: make time interchangeable
        """Graph of messages sent in current server over past 7 days\n"""
        with sql.connect(f'data/{ctx.guild.id}/stats.db') as conn:
            cursor = conn.cursor()
            cursor.execute( "SELECT datetime FROM activity WHERE DATE(datetime)"  # querying the db for datetime objects
                            " BETWEEN DATE('now','-7 day') AND DATE('now')")      # from the last 7 days

            dated_messages =    [date_time for date_time in cursor]  # Sqlite returns list of tuples
            dated_messages =    [datetime.fromisoformat(tup[0])          # thus these hoops we jump through
                                for tup in dated_messages]

        conn.close()

        before = datetime.today() - relativedelta(days=6)

        dated_messages = [dt.strftime('%a %d') for dt in dated_messages]

        x = [dt.strftime('%a %d') for dt in rrule(DAILY, count=7, dtstart=before)]
        y = {}
        for day in x:
            y[day] = dated_messages.count(day)

        y = list(y.values())

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set( ylabel="Message Count",
                title="Server Activity")
        ax.grid()
        fig.savefig(f'data/{ctx.guild.id}/graph.png')
        await ctx.send( content="This past week's server activity:\n",
                        file=File(f'data/{ctx.guild.id}/graph.png'))
        os.remove(f'data/{ctx.guild.id}/graph.png')

    @commands.command()
    async def top10(self, ctx):
        """Graph of top 10 chatters in current server\n"""
        guild = ctx.guild.id
        author = ctx.message.author
        bar_width = 0.15

        conn = sql.connect(f'data/{guild}/stats.db')
        cursor = conn.cursor()
        cursor.execute( "SELECT id, message_count FROM members"
                        " ORDER BY message_count DESC LIMIT 10")

        data = cursor.fetchall()
        users = [await self.id_to_member(user[0], ctx) for user in data[0:10]]
        names = [user.name for user in users]
        msg_count = [user[1] for user in data[0:10]]
        conn.commit()
        conn.close()

        x_axis = np.arange(len(names))
        fig, ax = plt.subplots()
        ax.grid(axis='y')
        ax.bar(x_axis, msg_count, bar_width)
        ax.set_ylabel('Message Count')
        ax.set_xmargin(5)
        ax.set_title('Top 10 Chatters')
        ax.set_xticks(x_axis)
        ax.set_xticklabels(names, rotation=25, rotation_mode='anchor')
        ax.tick_params(axis='x', labelsize=9, pad=25)

        # tight option because xtick labels get cut off otherwise, due to rotation
        fig.savefig(f'data/{guild}/graph.png', bbox_inches='tight')

        await ctx.send( content=f'The top chatters for the {ctx.guild} server:',
                        file=File(f'data/{guild}/graph.png'))
        os.remove(f'data/{guild}/graph.png')

        if author not in users:
            await ctx.send(f"Step it up, {author.mention}, you're not even on there :smirk:")

    @commands.command()
    async def servergrowth(self, ctx, time='year'):  # TODO: make time interchangeable
        """Graph of new users for current server over last 12 months\n"""
        date_of = datetime.now()
        guild = ctx.guild.id

        conn = sql.connect(f'data/{guild}/stats.db')
        cursor = conn.cursor()

        cursor.execute( "SELECT join_date FROM members"
                        " WHERE DATE(join_date) BETWEEN DATE('now', '-12 month') AND DATE('now')"
                        " ORDER BY join_date ASC")
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        dates = [date_of.fromisoformat(dates[0]) for dates in data]
        dates = [date_string.strftime('%b-%y') for date_string in dates]
        before = date_of
        before -= relativedelta(months=11)
        x = [dt.strftime('%b-%y') for dt in rrule(MONTHLY, count=12, dtstart=before)]
        y = {}
        for month in x:
            y[month] = dates.count(month)

        y = list(y.values())

        fig, ax = plt.subplots()
        ax.grid()
        ax.plot(x, y)
        ax.tick_params(axis='x', labelsize=7)
        ax.set( ylabel="Number of New Members",
                title="Server Growth")

        fig.savefig(f'data/{guild}/graph.png', bbox_inches='tight')

        await ctx.send( content=f'The growth of the {ctx.guild} server:',
                        file=File(f'data/{guild}/graph.png'))
        os.remove(f'data/{guild}/graph.png')


def setup(client):
    client.add_cog(Graphing(client))
