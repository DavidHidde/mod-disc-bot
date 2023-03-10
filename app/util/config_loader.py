import importlib
import json
import os
from copy import deepcopy
from typing import Any


class ConfigLoader:
    """Class for loading a MDB configuration and accompanying cogs from a directory"""

    KEYWORD_TOKEN = 'token'
    KEYWORD_COGS = 'cogs'
    KEYWORD_CLASS = 'class'

    def load_from_directory(self, base_path: str, subdirectories: list[str]) -> dict:
        """Load the default configuration from the pointed directories as a dict"""
        cogs = []
        for subdir in subdirectories:
            cogs += self.get_subdir_cog_configs(os.path.join(base_path, subdir))

        return {
            self.KEYWORD_TOKEN: None,
            self.KEYWORD_COGS: cogs
        }

    def load_from_file(self, file_path: str) -> dict:
        """Load the user made configuration from the file path"""
        with open(file_path, 'r') as config_file:
            return json.load(config_file)

    def get_merged_configs(self, base_path: str, subdirectories: list[str], file_path: str) -> dict:
        """Load a default config from the cogs and the user one from a file and merge them"""

        def __merge_configs(ground_truth: Any, override: Any) -> Any:
            """Merge configs by merging dictionaries. Fills in missing dict values, but assumes the override is correct otherwise"""
            if override is None:
                return ground_truth

            if type(ground_truth) is dict:
                if type(override) is dict:
                    return {key: __merge_configs(ground_truth.get(key), override.get(key)) for key, value in
                            ground_truth.items()}
                return ground_truth
            else:
                return override

        user_config = self.load_from_file(file_path)
        default_config = self.load_from_directory(base_path, subdirectories)

        # Merge cogs with preference for the default config, since it might hold new cog configs
        merged_cogs = []
        user_cogs = user_config.get(self.KEYWORD_COGS, [])
        for idx, cog_item in enumerate(default_config.get(self.KEYWORD_COGS, [])):
            if idx < len(user_cogs):
                merged_cogs.append(__merge_configs(cog_item, user_cogs[idx]))
            else:
                merged_cogs.append(cog_item)

        return {
            self.KEYWORD_TOKEN: user_config.get(self.KEYWORD_TOKEN, default_config.get(self.KEYWORD_TOKEN)),
            self.KEYWORD_COGS: merged_cogs
        }

    def get_subdir_cog_configs(self, root_path: str) -> list[dict]:
        """Get a list of configs of all cogs in the subdirectory"""
        for subdir in os.listdir(root_path):
            if os.path.isdir(os.path.join(root_path, subdir)) and \
                    not subdir.startswith('_') and \
                    not subdir.startswith('.'):
                cog_class = self.get_cog_class_from_directory(root_path, subdir)
                cog = cog_class(None, {})
                cog_config = cog.default_settings
                cog_config[self.KEYWORD_CLASS] = type(cog)
                yield cog_config

    def get_cog_class_from_directory(self, path: str, cog_name: str):
        """Get a cog class by importing the module from a directory"""
        module_name = os.path.join(path, cog_name).replace(os.sep, '.')
        cog_module = importlib.import_module(module_name)
        return getattr(cog_module, f'{cog_name}Cog')

    def save_config(self, config: dict, file_name: str) -> None:
        """Save a config file, ignoring non serializable fields"""
        copy_config = deepcopy(config)

        # Filter the class keyword since it's not serializable
        for cog in copy_config[self.KEYWORD_COGS]:
            del cog[self.KEYWORD_CLASS]

        with open(file_name, 'w') as config_file:
            json.dump(copy_config, config_file)
