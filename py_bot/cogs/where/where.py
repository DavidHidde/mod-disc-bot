import discord
import random
import os
import json

from cogs import CommandCog
from cogs.where.template_image import TemplateImage
from discord import app_commands, Interaction
from discord.ext.commands import Bot
from io import BytesIO
from PIL import ImageDraw, ImageFont


class WhereCog(CommandCog):
    """Where cog which can send funny images with funny text on it"""

    ASSETS_PATH = '/usr/assets/where'
    images: list

    def __init__(self, bot: Bot, **options):
        self.parse_images(bot)
        super().__init__(bot, **options)

    def parse_images(self, bot: Bot):
        """Pre-process images in the given directory"""
        try:
            with open(os.path.join(self.ASSETS_PATH, 'metadata.json')) as f:
                self.images = json.load(f)

            command_tree = bot.tree

            return True

        except Exception as e:
            self._logger.error(e)
            return False

    @app_commands.command()
    async def where(self, ctx: Interaction, text: str):
        """Send a random image from a template with specified text on it"""
        await ctx.response.defer()  # Defer since this might take long

        try:
            image_container = TemplateImage(random.choice(self.images))

            # Calculate font size
            fontsize = 1
            font = image_container.get_font(fontsize)
            final_text = image_container.get_completed_text(text)
            (box_width, box_height) = image_container.get_box_dimensions()
            (text_width, text_height) = self.get_text_box(final_text, font)

            while text_width < box_width and text_height < box_height:
                fontsize += 1
                font = image_container.get_font(fontsize)
                (text_width, text_height) = self.get_text_box(final_text, font)

            # Center text
            (origin_x, origin_y) = image_container.get_box_origin()
            origin_x += (box_width - text_width) / 2 if (box_width - text_width) > 0 else 0
            origin_y += (box_height - text_height) / 2 if (box_height - text_height) > 0 else 0

            # Draw font
            image = image_container.get_image()
            draw = ImageDraw.Draw(image)
            draw.text((origin_x, origin_y), final_text, font=font, fill=image_container.get_color())

            # Write image to discord without saving
            with BytesIO() as image_binary:
                image.save(image_binary, 'JPEG')
                image_binary.seek(0)
                return await ctx.followup.send(file=discord.File(fp=image_binary, filename='where.jpg'))

        except Exception as e:
            self._logger.error(e)
            return await ctx.followup.send(content='Something went wrong while trying to make the funny')

    @app_commands.command()
    async def find_images(self, ctx: Interaction):
        """Reprocess all images (only accessible by server owner)"""
        if not self._bot.is_owner(await self._bot.fetch_user(ctx.user.id)):
            return await ctx.response.send_message(content='Only the bot owner is allowed to do this ^^')

        await ctx.response.defer()
        if self.parse_images(self._bot):
            return await ctx.followup.send(content='Updated funny images')

        return await ctx.followup.send(content='Failed to update funny images :(')

    def get_text_box(self, text: str, font: ImageFont):
        """Calculate accurate text bounding box"""
        # https://stackoverflow.com/a/46220683/9263761
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text).getbbox()[2]
        text_height = font.getmask(text).getbbox()[3] + descent

        return text_width, text_height

