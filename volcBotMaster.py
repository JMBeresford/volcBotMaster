from discord.ext import commands
import psycopg2 as psql
import logging
import json
import os

try:
    f = open("config.json", "r")
except FileNotFoundError as e:
    print("Config file not found, please run configure.py first.\n")
    exit()

config = json.load(f)

f.close()

logger = logging.getLogger('discord')  # logging nonsense
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix=config['prefix'])
def_augments = ['Administrator', 'Moderator', 'Augmentation', 'General']  # default augments
client.owner_id = config['owner_id']
mod_role = config['mod_role']
admin_role = config['admin_role']


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
    """Reloads default augments\n"""
    if not await client.is_owner(ctx.author):
        await ctx.send(f'Only the bot owner can do that, {ctx.author.mention}')
    else:
        await ctx.send("Reloading default augments...")
        for filename in def_augments:
            client.reload_extension(f'augments.{filename}')


@client.command()
async def die(ctx):
    """This kills the crab, I mean, bot\n"""
    if not await client.is_owner(ctx.author):
        await ctx.send(f'Only the bot owner can do that, {ctx.author.mention}')
    else:
        await client.close()


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

"""
@client.event
async def on_command(ctx):  # permissions check
    command_list = {}
    conn = psql.connect(user = config['db_user'],
                            password = config['db_password'],
                            host = config['db_host'],
                            port = config['db_port'],
                            dbname = config['db_name'])

    cur = conn.cursor()

    cur.execute("SELECT command, clearance FROM commands;")

    data = cur.fetchone()
    try:
        command_list = dict(zip(data[0], data[1]))
    except TypeError:
        pass

    if ctx.command not in command_list:
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

    conn.close()
"""

@client.event
async def on_command_error(ctx, error):
    if error is commands.errors.MissingRequiredArgument:
        await ctx.send("Syntax Error: Try `?help <command>`")


client.run(config['token'])
