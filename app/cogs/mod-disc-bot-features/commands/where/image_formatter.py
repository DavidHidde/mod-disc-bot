from PIL import Image, ImageDraw, ImageFont

from .template_image import TemplateImage


class ImageFormatter:
    """Class that can format text on a Template image"""


    def apply_text_on_image(self, text: str, template_image: TemplateImage) -> Image:
        """Draw and format text on an image"""
        # Calculate font size
        fontsize = 1
        font = template_image.get_font(fontsize)
        final_text = template_image.get_completed_text(text)
        (box_width, box_height) = template_image.get_box_dimensions()
        (text_width, text_height) = self.get_text_box(final_text, font)

        while text_width < box_width and text_height < box_height:
            fontsize += 1
            font = template_image.get_font(fontsize)
            (text_width, text_height) = self.get_text_box(final_text, font)

        # Center text
        (origin_x, origin_y) = template_image.get_box_origin()
        origin_x += (box_width - text_width) / 2 if (box_width - text_width) > 0 else 0
        origin_y += (box_height - text_height) / 2 if (box_height - text_height) > 0 else 0

        # Draw font
        image = template_image.get_image()
        draw = ImageDraw.Draw(image)
        draw.text((origin_x, origin_y), final_text, font=font, fill=template_image.get_color())

        return image


    def get_text_box(self, text: str, font: ImageFont) -> tuple[int, int]:
        """Calculate accurate text bounding box"""
        # https://stackoverflow.com/a/46220683/9263761
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text).getbbox()[2]
        text_height = font.getmask(text).getbbox()[3] + descent

        return text_width, text_height
