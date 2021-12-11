import nextcord
import logging
import traceback
import json

from nextcord.ext import commands
from discord_ui import UI, SlashOption

from util import Extension, Cog

logger = logging.getLogger('nextcord-main')
logging.basicConfig(level=logging.DEBUG)

# Setup the bot classes
client = commands.Bot(" ")
ui = UI(client)

# Load cogs and extensions
secrets = json.load(open('secrets.json'))
try:
    for extension in secrets['extensions']:
        client.load_extension(Extension(**extension).get_path())

    for cog in secrets['cogs']:
        parsed_cog = Cog(**cog)
        cog_class = parsed_cog.get_class()
        client.add_cog(cog_class(client, secrets, **parsed_cog.get_options()))
except Exception as err:
    logger.debug(traceback.format_exc())
    logger.error(err)
    logger.error('Something went wrong while loading cogs/extensions. aborting...')
    exit(0)


@client.event
async def on_ready():
    logger.info('Bot ready to go')


@client.event
async def on_error(event, *args, **kwargs):
    """General error handling"""
    logger.error(f'Error caused by {event}')


@ui.slash.command("hello_world", guild_ids=[308355983745220619])
async def command(ctx, cool=True):
    """This is a simple slash command"""
    # you can use docstrings for the slash command description too
    logger.info(f'Yes I can read')
    await ctx.respond("You said this libary is " + str(cool))


# Run the bot
client.run(secrets['token'])
