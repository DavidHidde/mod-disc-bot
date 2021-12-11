import logging
import pickle

from os import path

import discord
from discord import Member, Colour, Role
from discord.ext import commands
from discord.utils import get


class FunnyRolesCog(commands.Cog):
    """Cog that allows for letting users add funny roles through commands"""

    bot: discord.Bot
    secrets: dict
    max_roles: int
    file_name: str
    user_credit: dict

    def __init__(self, bot, secrets, **options):
        self.bot = bot
        self.secrets = secrets
        self.max_roles = options.get('max_roles', 10)
        self.file_name = options.get('file_name', 'creditstore')
        self.user_credit = self.load_credit()
        self.logger = logging.getLogger('FunnyRolesCog')

        self.logger.info('Initialized funny roles cog')

    @commands.slash_command(name="give_role")
    async def give_role(self, ctx, user: Member, role_name: str):
        """Give a role to a user"""
        # Input parsing
        if not role_name or len(role_name) == 0 or role_name == ' ':
            return await ctx.respond('Missing argument role name')
        role_name = role_name.strip()

        # Check if author can give roles
        author = ctx.author
        if self.check_credit(author.id):
            return await ctx.respond('You have no role credit left')

        # Check if the role already exists, else create it
        guild = ctx.guild
        role = get(guild.roles, name=role_name)
        if role in user.roles:
            return await ctx.respond(f'{user.display_name} already has that role')
        if not role:
            role = await guild.create_role(name=role_name, colour=Colour.random())

        # Finally, add the role
        try:
            await user.add_roles(role)
            credit = self.user_credit.get(author.id, None)
            if credit:
                self.user_credit[author.id].append((role_name, user.id))
            else:
                self.user_credit[author.id] = [(role_name, user.id)]
        except Exception:
            return await ctx.respond(f"Couldn't give role '{role_name}' to {user.display_name}")

        self.save_credit()
        return await ctx.respond(f"Gave role '{role_name}' to {user.display_name}")

    @commands.slash_command(name="remove_role")
    async def remove_role(self, ctx, user: Member, role: Role):
        """Remove a role given by a user"""
        # Input parsing
        if not role:
            return await ctx.respond('Missing argument role name')

        # Check if the author gave that role to the target
        author = ctx.author
        user_credit = self.user_credit.get(author.id)
        if not user_credit or (role.name, user.id) not in user_credit:
            return await ctx.respond(f"You didn't give {user.display_name} that role")

        # Remove role
        try:
            await user.remove_roles(role)
            user_credit.remove((role.name, user.id))
            if not role.members:
                await role.delete()
            self.user_credit[author.id] = user_credit
        except Exception:
            return await ctx.respond(f"Couldn't remove role '{role.name}' from {user.display_name}")

        self.save_credit()
        return await ctx.respond(f"Removed role '{role.name}' from {user.display_name}")

    @commands.slash_command(name="role_credit")
    async def role_credit(self, ctx):
        """Check how many roles you can still give away"""
        if not self.user_credit:
            return await ctx.respond('No roles have been given away yet')

        author = ctx.author
        role_list = self.user_credit.get(author.id)
        count = len(role_list) if role_list else 0
        if count == 0:
            return await ctx.respond('You have not given away any role yet')

        # Display roles in a nice manner
        message = f'You have given away {count} roles:\n\n'
        for role, target in role_list:
            user = await self.bot.fetch_user(target)
            message += f" - '{role}' to {user.display_name}\n"
        return await ctx.respond(message + f'\nYou can still give away {self.max_roles - count} roles\n')

    def save_credit(self):
        """Save user_credit[] in file_name"""
        with open(self.file_name, 'wb') as credit_file:
            pickle.dump(self.user_credit, credit_file)
        self.logger.debug('Saved credits in file')

    def load_credit(self):
        """Load user_credit[] from file_name if it exists"""
        if path.exists(self.file_name):
            with open(self.file_name, 'rb') as credit_file:
                return pickle.load(credit_file)
        else:
            self.logger.debug('No credits file found')
            return {}

    def check_credit(self, user_id):
        """Check if the user is at max credit"""
        role_list = self.user_credit.get(user_id)
        return role_list is not None and len(role_list) >= self.max_roles
