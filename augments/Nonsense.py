import discord
import os
import discord
from discord.ext import commands

"""Self-explanatory name"""

# TODO: favoriteWord, favoriteCommand


class Nonsense(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        """Pongs your ping\n"""
        await ctx.send('Pong!')

    @commands.command()
    async def foo(self, ctx):
        """Bars your foo\n"""
        await ctx.send('Bar!')

    @commands.command()
    async def whisper(self, ctx, target: discord.Member, *, msg):
        """Have the bot whisper another user for you\n"""
        await target.send(f'{ctx.message.author} said: {msg}')

    @commands.command()
    async def penis(self, ctx, *targets: discord.Member):
        """The bot physically measures your length\n"""
        
        shafts = {}
        msg = ""
        
        for target in targets:
            if target.id == 174439608577294336:
                shafts[target.id] = f"8{'=' * 31}D"
                msg += f"{shafts[target.id]}\t<-{target.mention}'s length\n"
            else:
                length = target.id % 30
                shafts[target.id] = f"8{'=' * length}D"
                msg += f"{shafts[target.id]}\t<-{target.mention}'s length\n"

        await ctx.send(msg)

    @commands.command()
    async def textbooks(self, ctx, *, book_name='null'):
        books = []
        msg = ""
        for book in os.listdir(f'data/books/'):
            books.append(book)

        if book_name == 'null':
            if books.__len__ == 0:
                await ctx.send('There are no textbooks available.')

            else:
                for book in books:
                    msg += '`' + book + '`' + '\n\n'

                await ctx.send(content='The following books are available:\n')
                await ctx.send(msg)

        else:
            author = ctx.author
            await author.message(file=f"data/books/{book_name}")

def setup(client):
    client.add_cog(Nonsense(client))
