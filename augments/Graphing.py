from discord import File
import json
from discord.ext import commands
import psycopg2 as psql
import sqlite3 as sql
import os
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
from datetime import datetime, date

"""The logic for graphing is all implemented here"""


class Graphing(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = {}
        with open('config.json') as f:
            self.config = json.load(f)

    async def id_to_member(self, member_id, ctx):
        for member in ctx.guild.members:
            if member.id == int(member_id):
                return member
        return 'User Not Found'

    @commands.command()
    async def serveractivity(self, ctx, *, time='week'):
        """Graph of messages sent in current server over given time interval\n"""
        time = time.lower()
        timeframes = ('week', 'month', 'year')
        if time not in timeframes:
            await ctx.send("Please enter a valid timeframe ('week', 'month' 'year').")
            return

        day_span = 7 if time == 'week' else 31 if time == 'month' else 365
        before = datetime.today() - relativedelta(days=(day_span - 1))
        fmtstr = '%a %d' if time != 'year' else '%b %Y'
        rotation = 0
        pad = 0

        print("before:", before)

        try:
            connection = psql.connect(user = self.config['db_user'],
                                            password = self.config['db_password'],
                                            host = self.config['db_host'],
                                            port = self.config['db_port'],
                                            dbname = self.config['db_name'])
        except (Exception, psql.Error) as error:
            print(error)

        curr = connection.cursor()

        try:
            curr.execute('''SELECT sent_at
                            FROM messages
                            WHERE sent_at
                            <= timestamp 'now' AND
                            sent_at >= timestamp 'now' - interval '%s days' AND
                            guild_id = '%s';
                            ''', (day_span, ctx.guild.id))
        except (Exception, psql.Error) as error:
            print(error)

        dated_messages = [dt[0].strftime(fmtstr) for dt in curr]

        curr.close()
        connection.close()

        if time=='week':
            x = [dt.strftime(fmtstr) for dt in rrule(DAILY, count=7, dtstart=before)]
        elif time=='month':
            x = [dt.strftime(fmtstr) for dt in rrule(DAILY, count=31, dtstart=before)]
            rotation = 90
            pad = 20
        else:
            x = [dt.strftime(fmtstr) for dt in rrule(MONTHLY, count=12, dtstart=datetime.now() - relativedelta(months=11))]
        y = []

        print(x)
        if time != 'year':
            for day in range(0,day_span):
                delta = datetime.today() - relativedelta(days=day)
                print('delta:', delta)
                y.append(dated_messages.count(delta.strftime(fmtstr)))

        else:
            for month in range(0,12):
                delta = datetime.today() - relativedelta(months=month)
                print('delta:', delta)
                print('delta format:', delta.strftime(fmtstr))
                y.append(dated_messages.count(delta.strftime(fmtstr)))
        y.reverse()
        print(y)

        fig, ax = plt.subplots()
        ax.plot_date(x,y,fmt='-')
        ax.set( ylabel="Message Count",
                title="Server Activity")
        ax.set_xticklabels(x,rotation=rotation, rotation_mode='anchor')
        ax.tick_params(axis='x', labelsize=9, pad=pad)
        ax.grid()
        ax.autoscale()

        try:
            fig.savefig(f'data/{ctx.guild.id}/graph.png', bbox_inches='tight')
        except Exception as error:
            print(error)
        
        try:
            await ctx.send( content="This past week's server activity:\n",
                            file=File(f'data/{ctx.guild.id}/graph.png'))
        except Exception as error:
            print(error)
        
        os.remove(f'data/{ctx.guild.id}/graph.png')

    @commands.command()
    async def top10(self, ctx):
        """Graph of top 10 chatters in current server\n"""
        guild = ctx.guild.id
        author = ctx.message.author
        bar_width = 0.15
        config = self.config

        conn = psql.connect(user = config['db_user'],
                            password = config['db_password'],
                            host = config['db_host'],
                            port = config['db_port'],
                            dbname = config['db_name'])
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
