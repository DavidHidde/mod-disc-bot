import asyncio
import json
import logging
import traceback

import discord
from discord.ext.commands import Bot

from util import ConfigLoader

COG_ROOT_DIRECTORY = 'cogs'
COG_DIR_FILE = 'cogs.json'
CONFIGURATION_FILE = 'configuration.json'

logger = logging.getLogger('discord-main')
logging.basicConfig(level=logging.INFO)

# Setup the bot class
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = Bot('!/', intents=intents)


# Add cogs/extensions and start bot with token
async def main():
    async with bot:
        try:
            with open(COG_DIR_FILE, 'r') as cog_file:
                cog_dirs = json.load(cog_file).values()
            config_loader = ConfigLoader()
            config = config_loader.get_merged_configs(COG_ROOT_DIRECTORY, cog_dirs, CONFIGURATION_FILE)
            config_loader.save_config(config, CONFIGURATION_FILE)

            for cog_config in config[ConfigLoader.KEYWORD_COGS]:
                await bot.add_cog(cog_config[ConfigLoader.KEYWORD_CLASS](bot, cog_config))
        except Exception as err:
            logger.debug(traceback.format_exc())
            logger.error(err)
            logger.error('Something went wrong while loading config and cogs. Aborting...')
            exit(0)

        # Start the bot
        await bot.start(config[ConfigLoader.KEYWORD_TOKEN])


@bot.event
async def on_ready():
    # Update commands to be guild specific and sync them to guilds
    try:
        command_tree = bot.tree
        guilds = bot.guilds

        for guild in guilds:
            if guild is not None:
                logging.info(f"Syncing commands to guild {guild.name}")
                command_tree.copy_global_to(guild=guild)
                await command_tree.sync(guild=guild)

    except Exception as err:
        logger.debug(traceback.format_exc())
        logger.error(err)
        logger.error('Something went wrong while syncing commands. Aborting...')
        await bot.close()
        exit(0)

    logger.info('Bot ready to go')


@bot.event
async def on_error(event, *args, **kwargs):
    """General error handling"""
    logger.error(f'Error caused by {event}')
    logger.debug(traceback.format_exc())


asyncio.run(main())
