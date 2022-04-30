import logging
import traceback
import json
import discord
import asyncio

from discord.ext.commands import Bot
from util import Extension, Cog, AMSQL

logger = logging.getLogger('discord-main')
logging.basicConfig(level=logging.INFO)

# Setup the bot class
bot = Bot('!/', intents=discord.Intents.default())


# Add cogs/extensions and start bot with token
async def main():
    async with bot:
        secrets = json.load(open('secrets.json'))

        # Setup MYSLQ, load cogs and extensions
        try:
            AMSQL.set_settings(secrets.get('mysql'))

            for extension in secrets['extensions']:
                await bot.load_extension(Extension(**extension).get_path())

            for cog in secrets['cogs']:
                parsed_cog = Cog(**cog)
                cog_class = parsed_cog.get_class()
                await bot.add_cog(cog_class(bot, **parsed_cog.get_options()))

        except Exception as err:
            logger.debug(traceback.format_exc())
            logger.error(err)
            logger.error('Something went wrong while loading cogs/extensions. aborting...')
            exit(0)

        # Start the bot
        await bot.start(secrets['token'])


@bot.event
async def on_ready():
    try:
        command_tree = bot.tree

        for guild in bot.guilds:
            if guild is not None:
                logging.info(f"Syncing commands to guild {guild.name}")
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
