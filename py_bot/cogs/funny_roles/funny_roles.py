import discord
import traceback

from util import AMSQL
from cogs import CommandCog
from discord import Member, Colour, Role, app_commands
from discord.ext.commands import Bot
from discord.utils import get
from .queries import *


class FunnyRolesCog(CommandCog):
    """Cog that allows for letting users add funny roles through commands"""

    max_roles: int
    banned_roles: set

    def __init__(self, bot: Bot, **options):
        self.max_roles = options.get('max_roles', 10)
        self.banned_roles = set(options.get('banned_roles', []))
        super().__init__(bot, **options)

    @app_commands.command()
    async def give_role(self, ctx: discord.Interaction, user: Member, role_name: str):
        """Give a role to a user"""
        # Input parsing
        if not role_name or len(role_name) == 0 or role_name == ' ':
            return await ctx.response.send_message(content='Missing argument: role name')
        role_name = role_name.strip()

        if role_name in self.banned_roles:
            return await ctx.response.send_message(content='You are not allowed to assign that role')

        await ctx.response.defer()
        # Check if author can give roles
        author = ctx.user
        if self.check_credit(author.id):
            return await ctx.followup.send(response='You have no role credit left')

        # Check if the role already exists, else create it
        guild = ctx.guild
        role = get(guild.roles, name=role_name)

        try:
            with AMSQL.get_conn().cursor() as conn:
                if not role:
                    role = await guild.create_role(name=role_name, colour=Colour.random())
                    conn.execute(CREATE_ROLE_QUERY, [role.id, role_name])

                if role in user.roles:
                    return await ctx.followup.send(content=f'{user.display_name} already has that role')

                # Finally, add the role to the user
                author_member_id = self.select_or_create_member(author)
                victim_member_id = self.select_or_create_member(user)

                conn.execute(CREATE_ROLE_RELATION_QUERY, [author_member_id, victim_member_id, role.id])

                await user.add_roles(role)
                AMSQL.get_conn().commit()
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
        # Check if the author gave that role to the target
        author = ctx.user
        try:
            with AMSQL.get_conn().cursor() as conn:
                conn.execute(SELECT_ROLE_AUTHOR_QUERY, [role.id, author.id, user.id])

                result = conn.fetchone()
                if not result:
                    return await ctx.followup.send(content=f"You didn't give {user.display_name} that role")

                (relation_id,) = result

                # Remove role from the user
                conn.execute(DELETE_ROLE_RELATION_QUERY, [relation_id])
                await user.remove_roles(role)

                # Remove unused roles
                if not role.members:
                    conn.execute(DELETE_UNUSED_ROLE_QUERY, [role.id])
                    await role.delete()

                AMSQL.get_conn().commit()
                return await ctx.followup.send(content=f"Removed role '{role.name}' from {user.display_name}")
        except Exception as e:
            self._logger.error(e)
            self._logger.debug(traceback.format_exc())
            return await ctx.followup.send(content=f"Something went wrong while trying to remove a role")

    @app_commands.command()
    async def role_credit(self, ctx: discord.Interaction):
        """Check how many roles you can still give away"""
        await ctx.response.defer()
        try:
            with AMSQL.get_conn().cursor() as conn:
                conn.execute(SELECT_GIVEN_ROLES_QUERY, [ctx.user.id])
                role_list = conn.fetchall()
                count = len(role_list) if role_list else 0
                if count == 0:
                    return await ctx.followup.send(content='You have not given away any role yet')

                # Display roles in a nice manner
                message = f'You have given away {count} roles:\n\n'
                for victim_id, role in role_list:
                    user = await self._bot.fetch_user(victim_id)
                    message += f" - '{role}' to {user.display_name}\n"

                message += f"\nYou can still give away {self.max_roles - count} roles\n"
                return await ctx.followup.send(content=message)
        except Exception as e:
            self._logger.error(e)
            self._logger.debug(traceback.format_exc())
            return await ctx.followup.send(content=f"Something went wrong while checking role credit")

    def check_credit(self, user_id: int):
        """Check if the user is at max credit"""
        with AMSQL.get_conn().cursor() as conn:
            conn.execute(SELECT_COUNT_GIVEN_ROLES_QUERY, [user_id])
            result = conn.fetchone()
            return not result or result[0] >= self.max_roles

    def select_or_create_member(self, member: Member):
        """Select or create a discord member in the DB. Return the ID"""
        with AMSQL.get_conn().cursor() as conn:
            conn.execute(SELECT_MEMBER_QUERY, [member.id])
            result = conn.fetchone()

            if not result:
                conn.execute(CREATE_MEMBER_QUERY, [
                    member.guild.id,
                    member.id,
                    member.name,
                    member.discriminator,
                    member.bot
                ])
                member_id = conn.lastrowid
            else:
                (member_id,) = result

            return member_id
