import discord
from discord.ext import commands
import json


class Moderator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mods = {}
        self.mod_role = 'BotMechanic'

        for guild in self.client.guilds:
            self.mods[guild.id] = [member.id for member in guild.members
                                   if self.mod_role in str(member.roles)]

            with open(f'data/{guild.id}/mods', 'w+') as file:
                json.dump(self.mods, file)

        print(f'\t\tLoaded Moderator augments successfully.\n')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if self.mod_role in str(after.roles) and self.mod_role not in str(before.roles):
            self.mods[after.guild.id].append(after.id)
            print(f'{str(after)} has been appointed as a Moderator.')

            with open('data/mods.json', 'w') as file:
                json.dump(self.mods, file)

        elif self.mod_role in str(before.roles) and self.mod_role not in str(after.roles):
            del self.mods[after.guild.id][self.mods[after.guild.id].index(after.id)]
            print(f'{str(after)} has been removed as a Moderator.')
            with open('data/admins.json', 'w') as file:
                json.dump(self.mods, file)

        else:
            pass

    @commands.command()
    async def purge(self, ctx, amount, target: discord.Member):
        def target_acquired(msg):
            return msg.author == target

        message_murder = await ctx.message.channel.purge(limit=int(amount), check=target_acquired,
                                                         before=ctx.message)

        await ctx.send(f"Purged {len(message_murder)} of {target.mention}'s messages.")

    @commands.command()
    async def kick(self, ctx, target: discord.Member, *, because='because reasons'):
        await target.kick(reason=because)

        await ctx.send('Get :clap: him :clap: outta :clap: here :clap:')


def setup(client):
    client.add_cog(Moderator(client))
