import re

from io import BytesIO
from aiohttp import ClientSession

from cogs import CommandCog
from discord import app_commands, Interaction, File


class QuoteCog(CommandCog):
    """Cog that implements commands containing quotes"""

    QUOTE_URL: str = 'https://inspirobot.me/api?generate=true'
    EXPECTED_URL_REGEX: str = r'https://generated\.inspirobot\.me/a/^\.jpg$'

    @app_commands.command()
    async def quote(self, ctx: Interaction):
        """Generate a random quote from the infinite wisdom of the internet"""
        await ctx.response.defer()

        # Request data link and create
        async with ClientSession() as session:
            image_url = None

            # Get image url
            async with session.get(self.QUOTE_URL) as response:
                image_url = await response.text()

                if response.status != 200 or self.is_bad_link(image_url):
                    self._logger.error('Failed fetching image link: ' + await response.text())
                    return await ctx.followup.send(content='Failed creating wisdom from thin air')

            # Get image and send it
            async with session.get(image_url) as response:
                if response.status != 200:
                    self._logger.error('Failed fetching image: ' + await response.text())
                    return await ctx.followup.send(content='Failed creating wisdom from thin air')

                data = BytesIO(await response.read())
                await ctx.followup.send(file=File(data, 'quote.jpg'))

    def is_bad_link(self, link: str) -> bool:
        """Check if the link links to an image"""
        return link is None or not link.startswith('https://generated.inspirobot.me/a') or not link.endswith('.jpg')