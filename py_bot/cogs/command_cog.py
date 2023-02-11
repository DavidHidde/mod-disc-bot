import logging

from discord.ext.commands import Bot, Cog


class CommandCog(Cog):
    """Simple cog that is used for creating discord application commands"""

    _bot: Bot
    _logger: logging.Logger

    def __init__(self, bot: Bot, **options):
        """Set bot attribute and create logger"""
        self._bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('Initialized ' + self.__class__.__name__)
