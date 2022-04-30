import logging
import discord
import random
import os
import io
import json

from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import Cog
from discord import app_commands


class WhereCog(Cog):
    """Where cog"""

    bot: discord.ext.commands.Bot
    logger: logging.Logger
    image_path: str
    images: list

    def __init__(self, bot: discord.ext.commands.Bot, **options):
        self.bot = bot
        self.logger = logging.getLogger('WhereCog')
        self.image_path = options.get('image_path')
        self.parse_images()
        self.logger.info('Initialized where cog')

    def parse_images(self):
        """Pre-process images in the given directory"""
        try:
            with open(os.path.join(self.image_path, 'metadata.json')) as f:
                self.images = json.load(f)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    @app_commands.command()
    @app_commands.guilds(308355983745220619)
    async def where(self, ctx: discord.Interaction, text: str):
        """Where he at"""
        await ctx.response.defer()
        text = ('where ' + text).lower()

        try:
            image_data = random.choice(self.images)
            image = Image.open(os.path.join(self.image_path, image_data.get('path')))

            # Get bounding box
            [origin_x, origin_y] = image_data.get('top_left_box', [0, 0])
            [end_x, end_y] = image_data.get('bottom_right_box', [image.width - 1, image.height - 1])
            text_width = end_x - origin_x
            text_height = end_y - origin_y

            # Calculate font size
            fontsize = 1
            font_path = os.path.join(self.image_path, 'arial.ttf')
            font = ImageFont.truetype(font_path, fontsize)

            while font.getsize(text)[0] < text_width and font.getsize(text)[1] < text_height:
                fontsize += 1
                font = ImageFont.truetype(font_path, fontsize)

            fontsize -= 1
            font = ImageFont.truetype(font_path, fontsize)

            # Center text
            origin_x += max(text_width - font.getsize(text)[0], 2) / 2
            origin_y += max(text_height - font.getsize(text)[1], 2) / 2

            # Draw font
            draw = ImageDraw.Draw(image)
            draw.text((origin_x, origin_y), text, font=font, fill=image_data.get('text_color', '#FFFFFF'))

            with io.BytesIO() as image_binary:
                image.save(image_binary, 'JPEG')
                image_binary.seek(0)
                return await ctx.followup.send(file=discord.File(fp=image_binary, filename='where.jpg'))
        except Exception as e:
            self.logger.error(e)
            return await ctx.followup.send(content='Something wong')

    @app_commands.command()
    @app_commands.guilds(308355983745220619)
    async def find_images(self, ctx: discord.Interaction):
        """Reprocess all images (only accessible by server owner)"""
        if not self.bot.is_owner(await self.bot.fetch_user(ctx.user.id)):
            return await ctx.response.send_message(content='Not allowed >:(')

        await ctx.response.defer()
        if self.parse_images():
            return await ctx.followup.send(content='Updated funny images')

        return await ctx.followup.send(content='Failed to update funny images :(')


