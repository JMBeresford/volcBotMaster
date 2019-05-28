import discord
from discord.ext import commands
import logging
import json

with open('token.json') as ifs:  # Takes bot token from file
    token = json.load(ifs)

logger = logging.getLogger('discord')  # logging nonsense
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix='?')
def_augments = ['Administrator', 'Moderator', 'Augmentation']  # always-on augments


@client.event
async def on_ready():
    """Start-up procedure"""
    print('Successfully logged on to Discord as {0.user}'.format(client))

    for guild in client.guilds:
        print(f'\tAccessing server: {guild}\n')

    for filename in def_augments:
        client.load_extension(f'augments.{filename}')
        print(f'\t\tLoaded {filename} augments successfully.\n')


client.run(token)
