from importlib import import_module
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
        module = import_module(module_name)
        return getattr(module, self.cog_class)

    def get_options(self):
        return self.options
