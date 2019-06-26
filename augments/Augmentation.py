from discord.ext import commands
import json
import os

"""This augment contains all functionality for enabling/disabling augments on a global-scale
   Adding server-specific augmentation is currently not planned and likely will not be due to
   impracticality, though I may implement blacklisting of specific augments on a per server
   basis in the future."""


class Augmentation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.default_augments = ['Administrator', 'Moderator', 'Augmentation', 'General']  # always-on augments

        with open('data/user_augs.json', 'r+') as file:  # checks for predefined settings
            self.user_augments = json.load(file)             # for non-default augments

        for aug, installed in self.user_augments.items():
            if installed:
                try:
                    self.client.load_extension(f'augments.{aug}')
                except commands.ExtensionAlreadyLoaded:
                    pass
                else:
                    print(f'\t\tLoaded {aug} user augments successfully.\n')

        for filename in os.listdir('./augments'):
            if filename.endswith('.py'):
                if filename[:-3] not in self.user_augments.keys():
                    if filename[:-3] not in self.default_augments:
                        self.user_augments[filename] = 0
                        print(f'New augments installed: {filename[:-3]}')

        print(f'\t\tLoaded Augmentation augments successfully.\n')

    async def is_default(self, aug):
        return aug in self.default_augments

    async def update_aug_persistence(self):
        with open('data/user_augs.json', 'w') as file:
            json.dump(self.user_augments, file)

    @commands.command()
    async def augment(self, ctx, aug):
        try:
            self.client.load_extension(f'augments.{aug}')
        except commands.ExtensionNotFound:
            await ctx.send(f"I could not find any '{aug}' augments. Check you're spelling? :smirk:")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"The '{aug}' augments are already loaded, genius.")
        else:
            await ctx.send(f'I have loaded {aug} augments.')
            self.user_augments[aug] = 1
            await self.update_aug_persistence()

    @commands.command()
    async def deaugment(self, ctx, aug):
        if await self.is_default(aug):
            await ctx.send(f'{aug} augments cannot be unloaded.')
        else:
            try:
                self.client.unload_extension(f'augments.{aug}')
            except commands.ExtensionNotLoaded:
                await ctx.send(f"There are no '{aug}' augments loaded.")
            else:
                self.user_augments[aug] = 0
                await self.update_aug_persistence()
                await ctx.send(f'I have unloaded {aug} augments.')


def setup(client):
    client.add_cog(Augmentation(client))
