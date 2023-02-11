import importlib
import mysql.connector

from dataclasses import dataclass


@dataclass
class Cog:
    """Dataclass representing a loadable cog"""
    file_name: str
    cog_class: str
    options: dict

    COG_PATH: str = 'cogs'

    def __init__(self, **kwargs):
        self.file_name = kwargs.get('name')
        self.cog_class = kwargs.get('class')
        self.options = kwargs.get('options', {})

        if not self.file_name or not self.cog_class:
            raise IOError('Cog has no name/class')

    def get_class(self):
        """Dynamically load the cog class"""
        module_name = '.'.join([self.COG_PATH, self.file_name, self.file_name])
        module = importlib.import_module(module_name)
        return getattr(module, self.cog_class)

    def get_options(self):
        return self.options


@dataclass
class Extension:
    """Dataclass representing a loadable extension"""
    file_name: str

    EXTENSION_PATH: str = 'extensions'

    def __init__(self, **kwargs):
        self.file_name = kwargs.get('name')

        if not self.file_name:
            raise IOError('Extensions has no name')

    def get_path(self):
        """Get the loadable extension path"""
        return '.'.join([self.EXTENSION_PATH, self.file_name, self.file_name])


class AMSQL:
    """Class that provides static methods for mysql connectors"""
    settings: dict = {}
    conn = None

    @staticmethod
    def get_conn():
        """Get or create a new buffered DB cursor connection"""
        if not AMSQL.conn:
            AMSQL.conn = mysql.connector.connect(**AMSQL.settings)

        if not AMSQL.conn.is_connected():
            AMSQL.conn.close()
            AMSQL.conn = mysql.connector.connect(**AMSQL.settings)

        return AMSQL.conn

    @staticmethod
    def set_settings(settings: dict):
        """Set the global settings for the class"""
        AMSQL.settings = {
            'host': settings.get('host', 'mysql-db'),
            'user': settings.get('user', 'root'),
            'password': settings.get('password', ''),
            'db': settings.get('db', None)
        }
