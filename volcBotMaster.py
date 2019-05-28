import discord
from discord.ext import commands
import logging
import json

with open('token.json') as ifs: # Takes bot token from file
    token = json.load(ifs)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix = '?')

@client.event
async def on_ready():
    """Start-up procedure"""
    print('Successfully logged on to Discord as {0.user}'.format(client))

    for guild in client.guilds:
        print('\tAccessing server: ' + str(guild) + '\n')


""" COMMANDS """

# For fun commands
@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

@client.command()
async def foo(ctx):
    await ctx.send('Bar!')

@client.command()
async def whisper(ctx, target : discord.Member, *, msg):
    await target.send(ctx.message.author.name + ctx.message.author.discriminator + ' said: ' + msg)



# Moderator Commands
@client.command()
async def purge(ctx, amount, target : discord.Member):
    def targetAquired(msg):
        return True if msg.author == target else False

    messageMurder = await ctx.message.channel.purge(limit=100, check=targetAquired, before=ctx.message)

    await ctx.send("Purged {} of {}'s messages.".format(len(messageMurder), target.name))

@client.command()
async def kick(ctx, target : discord.Member, *, because='because reasons'):
    await target.kick(reason=because)

    await ctx.message.channel.send('Get :clap: him :clap: outta :clap: here :clap:')


client.run(token)