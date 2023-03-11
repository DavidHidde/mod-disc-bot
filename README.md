# Mod-Disc-Bot 
A modular Python based Discord bot.

## Overview
Mod-Disc-Bot is a `discord.py` based Discord bot framework running on Docker, utilizing `Cogs` to add functionality to the base framework. Cogs in this framework are free to have their own containers and package dependencies using common declarative formats(Docker Compose and `requirements.txt`), and extensions of `discord.py`'s Cogs. 

The bot itself can be configured using a `configuration.json` file, which allows for changing behaviour without having to recreate and rebuild the bot containers. This file can be constructed from settings provided by all Cogs, and is bind-mounted allowing for live-reloading the bot. 

This framework does not come with any Cogs of its own, but is instead separated into a [separate repository](https://github.com/DavidHidde/mod-disc-bot-features). This repository is added as a submodule. These features are not necessary for the framework to function, but provide examples for how the framework can be used as a a backlog of already exisitng features.

The bot can be easily started using the `start_bot.sh` script with the optional `--build` flag. This starts the main Docker container and Docker containers of all **enabled** Cogs. `stop_bot.sh` can be used to take down all running containers based on the configuration, 

## Setup
To run the bot for the first time, a `cogs.json` and `configuration.json` file should be created in the project root. These can simply be copied from there respective templates, where the correct Cog repositories should be listed in the `cogs.json` file. To get the default configuration of the bot, run `start_bot.sh --build` followed by a `stop_bot.sh`. Afterwards, fill in at least the Discord `token` and the bot is ready to go! 

## Cog requirements
For the Cogs to function within the MDB framework, a couple of requirements are in place to make sure to allow for easy development.

### Cog classes
* Cog class constructors must accept the `Bot` and `settings` parameters, setting the Discord Bot and configurable settings dictionary. 
* Cogs must specify their default settings in a `default_settings` property, which is a dictionary containing at least the `name` and `enabled` properties. `name` should match the package name.
* Cogs should specify their dependencies on other cogs in a `get_required_extensions()` method, which is a list of Cog names the Cog depends on.

### Cog packages
* Cog classes must be placed in their own package, with the Cog class being able to be imported from the **package** using `<path_to_package>.<package_name>.<package_name>Cog`. This can be done in the `__init__.py` of the package.
* Cog packages that require `pip` dependencies must contain a `requirements.txt` file in the package directory.
* Cog packages that require extra docker containers must contain a `docker` folder in the package directory containing at least a `docker-compose.yml` file.

### Cog repositories
* Cog repositories should contain Cog packages, where each folder in the repository represents a Cog package unless prefixed by "`_`" or "`.`".
* Cog repositories must be listed in the `cogs.json` file in the root of the project, see `cog_template.json` for an example.
