import discord
from discord.ext import commands
import logging
import json

with open('token.json', 'r') as file:  # Takes bot token from file
    token = json.load(file)

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
    print(f'Successfully logged on to Discord as {client.user}')

    for guild in client.guilds:
        print(f'\tAccessing server: {guild}\n')

    for filename in def_augments:
        client.load_extension(f'augments.{filename}')


client.run(token)
