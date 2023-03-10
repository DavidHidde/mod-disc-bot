import json
import os
import random
from io import BytesIO
from typing import Union

import discord
from discord import Interaction, app_commands

from .image_formatter import ImageFormatter
from .template_image import TemplateImage
from ...mdb_cog import MDBCog


class WhereCog(MDBCog):
    """Where cog which can send funny images with funny text on it"""

    _name: str = 'where'
    __images: Union[list[TemplateImage], None] = None


    @property
    def images(self) -> list[TemplateImage]:
        """Lazy parser for all images"""
        if not self.__images:
            try:
                with open(os.path.join(self.assets_path, 'metadata.json')) as f:
                    self.__images = [TemplateImage(image_dict) for image_dict in json.load(f)]

            except Exception as e:
                self._logger.error(e)
                self.__images = []

        return self.__images


    @app_commands.command()
    async def where(self, ctx: Interaction, text: str):
        """Send a random image from a template with specified text on it"""
        await ctx.response.defer()  # Defer since this might take long

        try:
            template_image = random.choice(self.images)
            image_formatter = ImageFormatter()
            image = image_formatter.apply_text_on_image(text, template_image)

            # Write image to Discord directly
            with BytesIO() as image_binary:
                image.save(image_binary, 'JPEG')
                image_binary.seek(0)
                return await ctx.followup.send(file=discord.File(fp=image_binary, filename='where.jpg'))

        except Exception as e:
            self._logger.error(e)
            return await ctx.followup.send(content='Something went wrong while trying to make the funny')


    def get_required_extensions(self) -> list[str]:
        """Get a list of extensions that are required to run this cog"""
        return []
