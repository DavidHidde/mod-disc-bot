import logging
import discord
import traceback

from util.util_classes import AMSQL
from discord import Member, Colour, Role, app_commands
from discord.ext.commands import Cog
from discord.utils import get


class FunnyRolesCog(Cog):
    """Cog that allows for letting users add funny roles through commands"""

    bot: discord.ext.commands.Bot
    max_roles: int
    logger: logging.Logger

    def __init__(self, bot, **options):
        self.bot = bot
        self.max_roles = options.get('max_roles', 10)
        self.logger = logging.getLogger('FunnyRolesCog')

        self.logger.info('Initialized funny roles cog')

    @app_commands.command()
    async def give_role(self, ctx, user: Member, role_name: str):
        """Give a role to a user"""
        # Input parsing
        if not role_name or len(role_name) == 0 or role_name == ' ':
            return await ctx.response.send_message(content='Missing argument: role name')
        role_name = role_name.strip()

        # Check if author can give roles
        author = ctx.user
        if self.check_credit(author.id):
            return await ctx.response.send_message(response='You have no role credit left')

        # Check if the role already exists, else create it
        guild = ctx.guild
        role = get(guild.roles, name=role_name)

        try:
            with AMSQL.get_conn().cursor() as conn:
                if not role:
                    role = await guild.create_role(name=role_name, colour=Colour.random())
                    query = """
                        INSERT INTO bot_guild_role (id, name)
                        VALUES (%s, %s)          
                    """
                    conn.execute(query, [role.id, role_name])

                if role in user.roles:
                    return await ctx.response.send_message(content=f'{user.display_name} already has that role')
                
                # Finally, add the role to the user
                author_member_id = self.select_or_create_member(author)
                victim_member_id = self.select_or_create_member(user)
                
                query = """
                        INSERT INTO member_bot_guild_role (
                            author_member_id, 
                            victim_member_id, 
                            role_id
                        ) VALUES (%s, %s, %s)          
                    """
                conn.execute(query, [author_member_id, victim_member_id, role.id])

                await user.add_roles(role)
                AMSQL.get_conn().commit()
                return await ctx.response.send_message(content=f"Gave role '{role_name}' to {user.display_name}")
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.format_exc())
            return await ctx.response.send_message(content=f"Something went wrong while trying to give a role")

    @app_commands.command()
    async def remove_role(self, ctx, user: Member, role: Role):
        """Remove a role you have given to a user"""
        # Input parsing
        if not user:
            return await ctx.response.send_message(content='Missing argument: user')
        if not role:
            return await ctx.response.send_message(content='Missing argument: role name')

        # Check if the author gave that role to the target
        author = ctx.user
        try:
            with AMSQL.get_conn().cursor() as conn:
                query = """
                    SELECT mbgr.id
                    FROM 
                        member_bot_guild_role mbgr
                        JOIN discord_member adm ON mbgr.author_member_id = adm.id
                        JOIN discord_member vdm ON mbgr.victim_member_id = vdm.id
                    WHERE 
                        mbgr.role_id = %s AND
                        adm.user_id = %s AND    
                        vdm.user_id = %s           
                """
                conn.execute(query, [role.id, author.id, user.id])

                result = conn.fetchone()
                if not (result):
                    return await ctx.response.send_message(content=f"You didn't give {user.display_name} that role")

                (relation_id, ) = result

                # Remove role from the user
                query = """
                    DELETE
                    FROM member_bot_guild_role mbgr
                    WHERE mbgr.id = %s         
                """
                conn.execute(query, [relation_id])
                await user.remove_roles(role)

                # Remove unused roles
                if not role.members:
                    query = """
                        DELETE
                        FROM bot_guild_role bgr
                        WHERE bgr.id = %s         
                    """
                    conn.execute(query, [role.id])
                    await role.delete()

                AMSQL.get_conn().commit()
                return await ctx.response.send_message(content=f"Removed role '{role.name}' from {user.display_name}")
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.format_exc())
            return await ctx.response.send_message(content=f"Something went wrong while trying to remove a role")

    @app_commands.command()
    async def role_credit(self, ctx):
        """Check how many roles you can still give away"""
        try:
            with AMSQL.get_conn().cursor() as conn:
                author = ctx.user
                query = """
                    SELECT vdm.user_id, bgr.name
                    FROM 
                        bot_guild_role bgr
                        JOIN discord_member adm ON adm.user_id = %s
                        JOIN member_bot_guild_role mbgr ON mbgr.author_member_id = adm.id
                        JOIN discord_member vdm ON vdm.id = mbgr.victim_member_id
                """
                conn.execute(query, [author.id])

                role_list = conn.fetchall()
                count = len(role_list) if role_list else 0
                if count == 0:
                    return await ctx.response.send_message(content='You have not given away any role yet')

                # Display roles in a nice manner
                message = f'You have given away {count} roles:\n\n'
                for victim_id, role in role_list:
                    user = await self.bot.fetch_user(victim_id)
                    message += f" - '{role}' to {user.display_name}\n"
                return await ctx.response.send_message(content=message + f'\nYou can still give away {self.max_roles - count} roles\n')
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.format_exc())
            return await ctx.response.send_message(content=f"Something went wrong while checking role credit")

    def check_credit(self, user_id: int):
        """Check if the user is at max credit"""
        with AMSQL.get_conn().cursor() as conn:
            query = """
                SELECT COUNT(*)
                FROM member_bot_guild_role
                WHERE author_member_id = %s
            """
            conn.execute(query, [user_id])

            result = conn.fetchone()
            return not result or result[0] >= self.max_roles

    def select_or_create_member(self, member: Member):
        """Select or create a discord member in the DB. Return the ID"""
        with AMSQL.get_conn().cursor() as conn:
            query = """
                SELECT dm.id
                FROM discord_member dm
                WHERE dm.user_id = %s    
            """
            conn.execute(query, [member.id])
            result = conn.fetchone()

            if not result:
                query = """
                    INSERT INTO discord_member (
                        guild_id,
                        user_id,
                        name,
                        discriminator,
                        is_bot
                    ) VALUES (%s, %s, %s, %s, %s)          
                """
                conn.execute(query, [
                    member.guild.id,
                    member.id,
                    member.name,
                    member.discriminator,
                    member.bot
                ])
                member_id = conn.lastrowid
            else:
                (member_id, ) = result

            return member_id

