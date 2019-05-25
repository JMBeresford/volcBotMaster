import discord
import logging
import json

with open('token.json') as ifs: # Takes bot token from file
    token = json.load(ifs)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

@client.event
async def on_ready():
    """Start-up procedure"""

    print('Successfully logged on to Discord as {0.user}'.format(client))

    for guild in client.guilds:
        print('\tAccessing server: ' + str(guild) + '\n')

@client.event
async def on_message(message):
    if message.author is not client.user:
        print('Message from {0.author}: {0.content}'.format(message))

    if message.content == "die":
        await message.channel.send(message.author.mention + ' no u die')
        


client.run(token)