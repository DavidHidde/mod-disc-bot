from dataclasses import dataclass


@dataclass
class Extension:
    """Dataclass representing a loadable extension"""
    file_name: str

    EXTENSION_PATH: str = 'extensions'

    def __init__(self, **kwargs):
        self.file_name = kwargs.get('name')

        if not self.file_name:
            raise IOError('Extensions has no name')

    def get_path(self):
        """Get the loadable extension path"""
        return '.'.join([self.EXTENSION_PATH, self.file_name, self.file_name])
