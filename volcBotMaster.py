from discord.ext import commands
import sqlite3 as sql
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
client.owner_id = 174439608577294336
mod_role = "BotMechanic"
admin_role = "BotOfficer"


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
    if not await client.is_owner(ctx.author):
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
async def on_command(ctx):  # permissions check
    guild = ctx.guild

    with sql.connect(f'data/{guild.id}/stats.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT command, clearance FROM commands")
        data = cursor.fetchone()
        command_list = zip(data[0], data[1])

        if command_list is [] or ctx.command not in command_list:
            return
        elif command_list[ctx.command] is 'moderator':
            if mod_role not in [str(role) for role in ctx.author.roles]:
                ctx.send('You do not have permission to use that command.')
            else:
                return
        elif command_list[ctx.command] is 'administrator':
            if admin_role not in [str(role) for role in ctx.author.roles]:
                ctx.send('You do not have permission to use that command.')
            else:
                return
        else:
            pass


client.run(token)
