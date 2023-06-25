import base64
import os
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont


class Text2Img:
    def __init__(self):
        self.font_name_regular = "./atlas/helpers/fonts/SourceSansPro-Light.ttf"
        self.font_name_bold = "./atlas/helpers/fonts/SourceSansPro-Regular.ttf"
        self.font_size = 20  # reduce font size for better mobile view
        self.color = "black"
        self.image_file = None
        self.padding = 100
        self.desired_width = 750  # reduce desired width for better mobile view
        self.line_spacing = 10  # add line spacing attribute

    def convert(self, text: str):
        font_regular = ImageFont.truetype(self.font_name_regular, self.font_size)
        font_bold = ImageFont.truetype(self.font_name_bold, self.font_size)

        # Wrap the text
        wrapped_text = self.wrap_text(text, font_bold, self.desired_width)

        # Create the image
        w, h = self.get_multiline_text_size(wrapped_text, font_regular, font_bold)
        image = Image.new(
            "RGBA", (w + 2 * self.padding, h + 2 * self.padding), (255, 255, 255)
        )
        draw = ImageDraw.Draw(image)

        # Draw the text
        draw.text(
            (self.padding, self.padding),
            wrapped_text,
            fill=self.color,
            font=font_regular,
        )

        # Save the image
        result = self.upload_imgur(image=image)
        return result

    def get_multiline_text_size(self, text, font_regular, font_bold):
        max_w = 0
        total_h = 0
        for line in text.split("\n"):
            line_w = font_regular.getsize(line)[0]
            max_w = max(max_w, line_w)
            total_h += (
                font_regular.getsize(line)[1] + self.line_spacing
            )  # add line spacing to total height
        return max_w, total_h

    def wrap_text(self, text, font, max_width):
        text_lines = []
        text_line = []
        words = text.split()

        for word in words:
            # Calculate the width of the line with the new word added
            new_line_width = font.getsize(" ".join(text_line + [word]))[0]

            if new_line_width > max_width:
                text_lines.append(" ".join(text_line))
                text_line = [word]
            else:
                text_line.append(word)

        if len(text_line) > 0:
            text_lines.append(" ".join(text_line))

        return "\n".join(text_lines)

    def upload_imgur(self, image) -> str:
        client_id = os.getenv("IMGUR_CLIENT")
        headers = {"Authorization": "Client-ID {}".format(client_id)}
        api_key = os.getenv("IMGUR_SECRET")
        url = "https://api.imgur.com/3/upload.json"

        img_file = BytesIO()
        assert image is not None
        image.save(img_file, "PNG")
        img_file.seek(0)
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        post_result = requests.post(
            url,
            headers=headers,
            data={
                "key": api_key,
                "image": img_base64,
                "type": "base64",
            },
        )
        return post_result.json()["data"]["link"]
