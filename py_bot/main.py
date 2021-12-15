import logging
import traceback
import json

from discord import Bot
from util import Extension, Cog, AMSQL

logger = logging.getLogger('discord-main')
logging.basicConfig(level=logging.INFO)

# Setup the bot classes
bot = Bot()

# Load cogs and extensions
secrets = json.load(open('secrets.json'))
try:
    AMSQL.set_settings(secrets.get('mysql'))

    for extension in secrets['extensions']:
        bot.load_extension(Extension(**extension).get_path())

    for cog in secrets['cogs']:
        parsed_cog = Cog(**cog)
        cog_class = parsed_cog.get_class()
        bot.add_cog(cog_class(bot, **parsed_cog.get_options()))
except Exception as err:
    logger.debug(traceback.format_exc())
    logger.error(err)
    logger.error('Something went wrong while loading cogs/extensions. aborting...')
    exit(0)


@bot.event
async def on_ready():
    logger.info('Bot ready to go')


@bot.event
async def on_error(event, *args, **kwargs):
    """General error handling"""
    logger.error(f'Error caused by {event}')
    logger.debug(traceback.format_exc())


# Run the bot
bot.run(secrets['token'])
