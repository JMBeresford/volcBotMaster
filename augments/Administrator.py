import discord
from discord.ext import commands
import json


class Administrator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.admins = {}
        self.admin_role = 'BotOfficer'

        for guild in self.client.guilds:
            self.admins[guild.id] = [member.id for member in guild.members
                                     if self.admin_role in str(member.roles)]

        with open('data/admins.json', 'w+') as file:
            json.dump(self.admins, file)

        print(f'\t\tLoaded Administrator augments successfully.\n')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.admin_role in str(after.roles) and self.admin_role not in str(before.roles):
            self.admins[after.guild.id].append(after.id)
            print(f'{str(after)} has been appointed as an Administrator.')
            with open('data/admins.json', 'w') as file:
                json.dump(self.admins, file)

        elif self.admin_role in str(before.roles) and self.admin_role not in str(after.roles):
            del self.admins[after.guild.id][self.admins[after.guild.id].index(after.id)]
            print(f'{str(after)} has been removed as an Administrator.')
            with open('data/admins.json', 'w') as file:
                json.dump(self.admins, file)

        else:
            pass

    @commands.command()
    async def ban(self, ctx, target: discord.Member, *, because='because reasons'):
        await target.ban(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')

    @commands.command()
    async def die(self, ctx):
        await ctx.send('Shutting down... :wave:')
        await self.client.close()


def setup(client):
    client.add_cog(Administrator(client))
