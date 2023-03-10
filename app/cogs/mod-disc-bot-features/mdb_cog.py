import logging
import os.path

from abc import abstractmethod

from discord.ext.commands import Bot, Cog


class MDBCog(Cog):
    """
    Cog that can be initialized withing the MDB framework.
    In this context, a cog is either a command cog or an extension cog
    """

    _bot: Bot
    _logger: logging.Logger
    _name: str = 'cog_name'
    _settings: dict

    def __init__(self, bot: Bot, settings: dict):
        """Set bot attribute and create logger"""
        self._bot = bot
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def assets_path(self) -> str:
        """Get the custom assets path. If the path does not exist, creates the path"""
        path = f'/usr/assets/{self.__class__.__name__}'

        if os.path.exists(path):
            os.mkdir(path)

        return path

    @property
    def default_settings(self) -> dict:
        """Get all configurable settings of a cog"""
        return {
            'name': self._name,
            'enabled': False
        }

    @abstractmethod
    def get_required_extensions(self) -> list[str]:
        """Get a list of extensions that are required to run this cog"""
        pass
