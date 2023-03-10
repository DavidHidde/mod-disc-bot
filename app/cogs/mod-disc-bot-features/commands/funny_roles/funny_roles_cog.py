import traceback

import discord
import mysql.connector
from discord import Member, Role, app_commands
from discord.ext.commands import Bot

from .role_manager import RoleManager
from ...mdb_cog import MDBCog


class FunnyRolesCog(MDBCog):
    """Cog that allows for letting users add funny roles through commands"""

    __KEYWORD_MAX_ROLES: str = 'max_roles'
    __KEYWORD_BANNED_ROLES: str = 'banned_roles'

    _name: str = 'funny_roles'

    @property
    def default_settings(self) -> dict:
        """Get all configurable settings of a cog"""
        return {
            **super().default_settings,
            self.__KEYWORD_MAX_ROLES: 10,
            self.__KEYWORD_BANNED_ROLES: [],

        }

    def get_required_extensions(self) -> list[str]:
        """Get a list of extensions that are required to run this cog"""
        return ['mysql']

    @app_commands.command()
    async def give_role(self, ctx: discord.Interaction, user: Member, role_name: str):
        """Give a role to a user"""
        # Input parsing
        role_name = role_name.strip()
        if not role_name:
            return await ctx.response.send_message(content='Missing argument: role name')
        if role_name in self._settings[self.__KEYWORD_BANNED_ROLES]:
            return await ctx.response.send_message(content='You are not allowed to assign that role')

        await ctx.response.defer()
        try:
            role_manager = RoleManager(self.get_db_connection())

            # Check if author can give roles
            author = ctx.user
            role_list = role_manager.get_given_roles(author.id)
            if len(role_list) >= self._settings[self.__KEYWORD_MAX_ROLES]:
                return await ctx.followup.send(response='You have no role credit left')
            if (user.id, role_name) in role_list:
                return await ctx.followup.send(content=f'{user.display_name} already has that role')

            await role_manager.give_role_to_user(role_name, user, author, ctx.guild)
            return await ctx.followup.send(content=f"Gave role '{role_name}' to {user.display_name}")
        except Exception as e:
            self._logger.error(e)
            self._logger.debug(traceback.format_exc())
            return await ctx.followup.send(content=f"Something went wrong while trying to give a role")

    @app_commands.command()
    async def remove_role(self, ctx: discord.Interaction, user: Member, role: Role):
        """Remove a role you have given to a user"""
        # Input parsing
        if not user:
            return await ctx.response.send_message(content='Missing argument: user')
        if not role:
            return await ctx.response.send_message(content='Missing argument: role name')

        await ctx.response.defer()
        try:
            role_manager = RoleManager(self.get_db_connection())

            # Check if the author gave that role to the target
            author = ctx.user
            if not (user.id, role.name) in role_manager.get_given_roles(author.id):
                return await ctx.followup.send(content=f"You didn't give {user.display_name} that role")

            await role_manager.remove_role_from_user(role, author.id, user)
            return await ctx.followup.send(content=f"Removed role '{role.name}' from {user.display_name}")
        except Exception as e:
            self._logger.error(e)
            self._logger.debug(traceback.format_exc())
            return await ctx.followup.send(content=f"Something went wrong while trying to remove a role")

    @app_commands.command()
    async def role_credit(self, ctx: discord.Interaction):
        """Check how many roles you can still give away"""
        await ctx.response.defer()
        role_manager = RoleManager(self.get_db_connection())
        try:
            role_list = role_manager.get_given_roles(ctx.user.id)
            count = len(role_list)

            # Base case: no roles given yet
            if count == 0:
                return await ctx.followup.send(content='You have not given away any role yet')

            # Display roles in a nice manner
            message = f'You have given away {count} roles:\n\n'
            for victim_id, role in role_list:
                user = await self._bot.fetch_user(victim_id)
                message += f" - '{role}' to {user.display_name}\n"

            message += f"\nYou can still give away {self._settings[self.__KEYWORD_MAX_ROLES] - count} roles\n"
            return await ctx.followup.send(content=message)
        except Exception as e:
            self._logger.error(e)
            self._logger.debug(traceback.format_exc())
            return await ctx.followup.send(content=f"Something went wrong while checking role credit")

    def get_db_connection(self) -> mysql.connector:
        """Get the connection to the database"""
        return self._bot.get_cog('mysql').connection
