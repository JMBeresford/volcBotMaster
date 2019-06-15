import discord
from discord.ext import commands
import logging
import json
import os

with open('token.json', 'r') as file:  # Takes bot token from file
    token = json.load(file)

logger = logging.getLogger('discord')  # logging nonsense
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix='?')
def_augments = ['Administrator', 'Moderator', 'Augmentation', 'General']  # default augments


async def new_guild(guild, startup=True):
    try:
        os.mkdir(f'data/{guild.id}')
    except FileExistsError:
        pass

    if not startup:
        for filename in def_augments:
            client.reload_extension(f'augments.{filename}')


@client.command()
async def reload(ctx):
    if ctx.author is not client.application_info():
        await ctx.send(f'Only the bot owner can do that, {ctx.author.mention}')
    else:
        for filename in def_augments:
            client.reload_extension(f'augments.{filename}')


@client.event
async def on_ready():
    """Start-up procedure"""
    print(f'Successfully logged on to Discord as {client.user}')

    for guild in client.guilds:
        print(f'\tAccessing server: {guild}\n')
        await new_guild(guild)

    for filename in def_augments:
        client.load_extension(f'augments.{filename}')


@client.event
async def on_guild_join(guild):
    await new_guild(guild, startup=False)


@client.event
async def on_command(ctx):
    guild = ctx.guild

    mods = open(f'data/{guild.id}/mods', 'r')
    admins = open(f'data/{guild.id}/admins', 'r')
    mod_cmds = open(f'data/{guild.id}/mod_commands', 'r')
    if ctx.command in mod_cmds:
        if ctx.author.id in mods or ctx.author.id in admins:
            admins.close()
            mods.close()
            return
        else:
            admins.close()
            mods.close()
            await ctx.send(f'{ctx.author.mention}, you do not have permission to do that.')

    admins.close()
    mods.close()
    mod_cmds.close()


client.run(token)
