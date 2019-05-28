import discord
from discord.ext import commands, tasks
import json
import os


class Augmentation(commands.Cog):
    def __init__(self, client):
        self.client = client

    default_augments = ['Administrator', 'Moderator', 'Augmentation']  # always-on augments
    with open('data/user_augs.json', 'r') as f_obj:  # checks for predefined settings for non-default augments
        user_augments = json.load(f_obj)

    async def is_default(self, aug):
        return True if aug in self.default_augments else False

    async def update_aug_persistence(self):
        with open('data/user_augs.json', 'w') as file:
            json.dump(self.user_augments, file)

    @commands.Cog.listener()
    async def on_ready(self):
        for aug, installed in self.user_augments.items():
            if installed:
                self.client.load_extension(f'augments.{aug}')
                print(f'\t\tLoaded {aug} augments successfully.\n')

        for filename in os.listdir('./augments'):
            if filename.endswith('.py'):
                if filename[:-3] not in self.user_augments.keys():
                    if not await self.is_default(filename[:-3]):
                        self.user_augments[filename] = 0
                        print(f'New augments installed: {filename[:-3]}')

    @commands.command()
    async def augment(self, ctx, aug):
        self.client.load_extension(f'augments.{aug}')
        self.user_augments[aug] = 1
        await self.update_aug_persistence()
        await ctx.send(f'I have loaded {aug} augments.')

    @commands.command()
    async def deaugment(self, ctx, aug):
        if await self.is_default(aug):
            await ctx.send(f'{aug} augments cannot be unloaded.')
        else:
            self.user_augments[aug] = 0
            await self.update_aug_persistence()
            self.client.unload_extension(f'augments.{aug}')
            await ctx.send(f'I have unloaded {aug} augments.')


def setup(client):
    client.add_cog(Augmentation(client))
