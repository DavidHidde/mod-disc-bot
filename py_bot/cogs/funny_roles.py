import logging
import pickle

from os import path
from nextcord import Colour
from nextcord.ext import commands
from nextcord.utils import get
from discord_ui.cogs import slash_command


class FunnyRolesCog(commands.Cog):
    """Cog that allows for letting users add funny roles through commands"""

    def __init__(self, bot, secrets, **options):
        self.bot = bot
        self.secrets = secrets
        self.max_roles = options.get('max_roles', 10)
        self.file_name = options.get('file_name', 'creditstore')

        self.load_credit()

    @slash_command(name="giverole")
    async def give_role(self, ctx, user, *, role_name: str):
        """Give a role to a user"""
        # Input parsing
        if not role_name or len(role_name) == 0 or role_name == ' ':
            return await ctx.send('Missing argument role name')
        role_name = role_name.strip()

        # Check if author can give roles
        author = ctx.message.author
        if self.check_credit(author.id):
            return await ctx.send('You have no role credit left')

        # Check if the role already exists, else create it
        guild = ctx.guild
        role = get(guild.roles, name=role_name)
        if role in user.roles:
            return await ctx.send(f'{user.display_name} already has that role')
        if not role:
            role = await guild.create_role(name=role_name, colour=Colour.random())

        # Finally, add the role
        try:
            await user.add_roles(role)
            credit = self.bot.user_credit.get(author.id, None)
            if credit:
                self.bot.user_credit[author.id].append((role_name, user.id))
            else:
                self.bot.user_credit[author.id] = [(role_name, user.id)]
        except Exception:
            return await ctx.send(f"Couldn't give role '{role_name}' to {user.display_name}")

        self.save_credit()
        return await ctx.send(f"Gave role '{role_name}' to {user.display_name}")

    @slash_command(name="removerole")
    async def remove_role(self, ctx, user, *, role_name: str):
        """Remove a role given by a user"""
        # Input parsing
        if not role_name or len(role_name) == 0 or role_name == ' ':
            return await ctx.send('Missing argument role name')
        role_name = role_name.strip()

        # Check if the author gave that role to the target
        author = ctx.message.author
        user_credit = self.bot.user_credit.get(author.id)
        if not user_credit or (role_name, user.id) not in user_credit:
            return await ctx.send(f"You didn't give {user.display_name} that role")

        # Remove role
        role = get(ctx.guild.roles, name=role_name)
        try:
            await user.remove_roles(role)
            user_credit.remove((role_name, user.id))
            if not role.members:
                await role.delete()
            self.bot.user_credit[author.id] = user_credit
        except Exception:
            return await ctx.send(f"Couldn't remove role '{role_name}' from {user.display_name}")

        self.save_credit()
        return await ctx.send(f"Removed role '{role_name}' from {user.display_name}")

    @slash_command(name="rolecredit")
    async def role_credit(self, ctx):
        """Check how many roles a user can still give away"""
        author = ctx.message.author
        role_list = self.bot.user_credit.get(author.id, None)
        count = len(role_list) if role_list else 0
        if count == 0:
            return await ctx.send('You have not given away any role yet')

        message = f'You have given away {count} roles:\n\n'
        for role, target in role_list:
            user = await self.bot.fetch_user(target)
            message += f" - '{role}' to {user.display_name}\n"
        return await ctx.send(message + f'\nYou can still give away {self.ma - count} roles\n')

    def save_credit(self):
        """Save user_credit[] in file_name"""
        with open(self.file_name, 'wb') as credit_file:
            pickle.dump(self.bot.user_credit, credit_file)
        logging.getLogger('FunnyRolesCog').info('Saved credits in file')

    def load_credit(self):
        """Load user_credit[] from file_name if it exists"""
        if path.exists(self.file_name):
            with open(self.file_name, 'rb') as credit_file:
                self.bot.user_credit = pickle.load(credit_file)
            logging.getLogger('FunnyRolesCog').info('Loaded credits')
        else:
            logging.getLogger('FunnyRolesCog').info('No credits file found')
            self.bot.user_credit = {}

    def check_credit(self, user_id):
        """Check if the user is at max credit"""
        role_list = self.bot.user_credit.get(user_id, None)
        return role_list != None and len(role_list) >= self.max_roles
