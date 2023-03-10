import os

from PIL import Image, ImageFont


class TemplateImage:
    """PIL Image container constructed from metadata"""

    IMAGE_FOLDER_PATH = '/usr/assets/where/img'
    FONT_FOLDER_PATH = '/usr/assets/where/font'

    __image: Image

    # Metadata
    __file_path: str  # Defaults to unknown.jpg
    __font_path: str  # Defaults to Arial

    __text_color: str  # Defaults to white
    __text_style: str  # Defaults to None
    __text_prefix: str  # Defaults to empty
    __text_suffix: str  # Defaults to empty

    __top_left_bb: tuple[int, int]  # Defaults to top left corner of the image
    __bot_right_bb: tuple[int, int]  # Defaults to bottom right corner of image


    def __init__(self, data: dict):
        """Construct the image template from provided metadata json dictionary"""
        self.__file_path = os.path.join(self.IMAGE_FOLDER_PATH, data.get('image', 'monke.jpg'))
        self.__font_path = os.path.join(self.FONT_FOLDER_PATH, data.get('font', 'arial.ttf'))

        self.__text_color = data.get('color', '#FFFFFF')
        self.__text_style = data.get('style', None)
        self.__text_prefix = data.get('prefix', '')
        self.__text_suffix = data.get('suffix', '')

        self.__image = Image.open(self.__file_path)

        self.__top_left_bb = tuple(data.get('top_left_box', [0, 0]))
        self.__bot_right_bb = tuple(data.get('bottom_right_box', [self.__image.width - 1, self.__image.height - 1]))


    def get_image(self) -> Image:
        """Get the PIL Image"""
        return self.__image


    def get_font(self, size: int) -> ImageFont:
        """Get text font with a certain size"""
        return ImageFont.truetype(self.__font_path, size)


    def get_color(self) -> str:
        """Get the text color"""
        return self.__text_color


    def get_completed_text(self, text: str) -> str:
        """Get a text styled, prefixed and suffixed"""
        complete_text = self.__text_prefix + text + self.__text_suffix

        if self.__text_style == 'uppercase':
            return complete_text.upper()
        if self.__text_style == 'lowercase':
            return complete_text.lower()

        return complete_text


    def get_box_dimensions(self) -> tuple[int, int]:
        """Get width and height of the bounding text box"""
        (origin_x, origin_y) = self.__top_left_bb
        (end_x, end_y) = self.__bot_right_bb
        return max(end_x - origin_x, 0), max(end_y - origin_y, 0)


    def get_box_origin(self) -> tuple[int, int]:
        """Get the starting point of the bounding box"""
        return self.__top_left_bb
