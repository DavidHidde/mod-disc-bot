import asyncio
import json
import logging
import traceback
from copy import copy

import discord
from discord.ext.commands import Bot, Context

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
bot = Bot('$', intents=intents)


def load_and_save_config() -> dict:
    """Load and save the config from the user file, merging it with cog configs"""
    with open(COG_DIR_FILE, 'r') as cog_file:
        cog_dirs = json.load(cog_file).values()
        config_loader = ConfigLoader()
    config = config_loader.get_merged_configs(COG_ROOT_DIRECTORY, cog_dirs, CONFIGURATION_FILE)
    config_loader.save_config(config, CONFIGURATION_FILE)

    return config


async def sync_commands() -> None:
    """Sync global commands to guild for easier development"""
    command_tree = bot.tree
    guilds = bot.guilds

    for command in command_tree.get_commands():
        logger.debug(f'Syncing command {command.name}')

    for guild in guilds:
        if guild is not None:
            logging.debug(f"Syncing commands to guild {guild.name}")
            command_tree.copy_global_to(guild=guild)
            await command_tree.sync(guild=guild)


async def main():
    """Add cogs/extensions and start bot with token"""
    async with bot:
        try:
            config = load_and_save_config()
            for cog_config in config[ConfigLoader.KEYWORD_COGS]:
                if cog_config['enabled']:
                    logging.debug(f"Adding cog {cog_config['name']}...")
                    await bot.add_cog(cog_config[ConfigLoader.KEYWORD_CLASS](bot, cog_config))
        except Exception as err:
            logger.debug(traceback.format_exc())
            logger.error(err)
            logger.error('Something went wrong while loading config and cogs. Aborting...')
            exit(0)

        # Start the bot
        await bot.start(config[ConfigLoader.KEYWORD_TOKEN])


@bot.hybrid_command()
async def reload_cog(ctx: Context, cog_id: str):
    """(Bot owner only) Reload a cog for the bot, adding it if it is not currently in the bot"""
    if not await bot.is_owner(ctx.author):
        return await ctx.send(content='Only the bot owner is allowed to run this command >:(')

    try:
        if bot.get_cog(cog_id):
            await bot.remove_cog(cog_id)

        config = load_and_save_config()

        cog_config = None
        for temp_cog_config in config[ConfigLoader.KEYWORD_COGS]:
            if temp_cog_config.get('name') == cog_id:
                cog_config = temp_cog_config
                break

        if not cog_config:
            return await ctx.send(content='The cog specified does not exist')

        if cog_config['enabled']:
            await bot.add_cog(cog_config[ConfigLoader.KEYWORD_CLASS](bot, cog_config))

        await ctx.send(
            content=f'Succesfully reloaded cog {cog_id}, please wait a bit for the changes to take effect'
        )
        await sync_commands()  # Sync after sending message to make sure we finish the request properly
    except Exception as err:
        logger.error(err)
        return await ctx.send(content='Something went wrong while reloading the cog')


@bot.hybrid_command()
async def full_reload(ctx: Context):
    """(Bot owner only) Unload the previous config and apply a new one"""
    if not await bot.is_owner(ctx.author):
        return await ctx.send(content='Only the bot owner is allowed to run this command >:(')

    # Load config, if something goes wrong here we can still abort
    try:
        config = load_and_save_config()
    except Exception as err:
        logger.debug(traceback.format_exc())
        logger.error(err)
        return await ctx.send(content='Something went wrong while loading the new config')

    # Remove all cogs and add all config cogs
    try:
        cogs_copy = copy(list(bot.cogs.keys()))
        for cog_id in cogs_copy:
            await bot.remove_cog(cog_id)

        for cog_config in config[ConfigLoader.KEYWORD_COGS]:
            if cog_config['enabled']:
                await bot.add_cog(cog_config[ConfigLoader.KEYWORD_CLASS](bot, cog_config))

        await ctx.send(content=f'Succesfully reloaded bot, please wait a bit for the changes to take effect')
        await sync_commands()  # Sync after sending message to make sure we finish the request properly
        logger.info('Reloaded bot')
    except Exception as err:
        logger.debug(traceback.format_exc())
        logger.error(err)
        return await ctx.send(content='Something went wrong while applying the new configuration')


@bot.event
async def on_ready():
    # Update commands to be guild specific and sync them to guilds
    try:
        await sync_commands()
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
