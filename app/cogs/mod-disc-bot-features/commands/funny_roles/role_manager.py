import mysql.connector
from discord import Member, Role, Guild, Colour
from discord.utils import get

from .queries import *


class RoleManager:
    """
    Class responsible for managing the roles of a user and persisting in the DB.
    Operations from this class may throw exceptions
    """

    __conn: mysql.connector

    def __init__(self, mysql_conn: mysql.connector):
        """Create a new manager given a bot and MySQL connector"""
        self.__conn = mysql_conn

    def create_db_tables_if_not_exists(self) -> None:
        """Create the DB tables if they do not exist"""
        with self.__conn.cursor() as cursor:
            cursor.execute(CREATE_TABLES_IF_NOT_EXISTS_QUERY)
            self.__conn.commit()

    async def give_role_to_user(self, role_name: str, user: Member, author: Member, guild: Guild) -> None:
        """Give a role to user. Create it if it does not exist"""
        with self.__conn.cursor() as cursor:
            # Create role if it does not exist
            role = get(guild.roles, name=role_name)
            db_role = cursor.execute(SELECT_ROLE_QUERY, [role_name]).fetchone()
            if not role:
                role = await guild.create_role(name=role_name, colour=Colour.random())
            if not db_role:
                cursor.execute(CREATE_ROLE_QUERY, [role.id, role_name])

            # Add the role to the user
            cursor.execute(
                CREATE_ROLE_RELATION_QUERY, [
                    self.select_or_create_member(author),
                    self.select_or_create_member(user),
                    role.id
                ]
            )

            await user.add_roles(role)
            self.__conn.commit()

    async def remove_role_from_user(self, role: Role, role_author_id: int, user: Member) -> None:
        """Remove a role from a user. If the role becomes unused, delete it"""
        with self.__conn.cursor() as cursor:
            # Remove role from the user
            cursor.execute(DELETE_ROLE_RELATION_QUERY, [role_author_id, user.id, role.id])
            await user.remove_roles(role)

            # Remove role if unused
            if not role.members:
                cursor.execute(DELETE_UNUSED_ROLE_QUERY, [role.id])
                await role.delete()

            self.__conn.commit()

    def select_or_create_member(self, member: Member):
        """Select or create a discord member in the DB. Return the ID"""
        with self.__conn.cursor() as cursor:
            cursor.execute(SELECT_MEMBER_QUERY, [member.id])
            result = cursor.fetchone()

            # Create member if it does not exist
            if not result:
                cursor.execute(
                    CREATE_MEMBER_QUERY, [
                        member.guild.id,
                        member.id,
                        member.name,
                        member.discriminator,
                        member.bot
                    ]
                )
                member_id = cursor.lastrowid
                self.__conn.commit()
            else:
                (member_id,) = result

            return member_id

    def get_given_roles(self, user_id: int) -> list[tuple[int, str]]:
        """Get a list of roles given by a user, given by (victim_id, role_name)"""
        with self.__conn.cursor() as cursor:
            cursor.execute(SELECT_GIVEN_ROLES_QUERY, [user_id])
            return cursor.fetchall()
