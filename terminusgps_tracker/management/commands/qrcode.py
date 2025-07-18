import argparse
import urllib.parse

import qrcode
from django.core.management.base import BaseCommand
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = "Creates QR code images for Wialon units by IMEI #."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds arguments to the command.

        :param parser: An argument parser.
        :type parser: :py:obj:`argparse.ArgumentParser`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        parser.add_argument("imei_numbers", nargs="+", type=int)

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :raises CommandError: If an IMEI # wasn't found in Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        for imei in options["imei_numbers"]:
            qr = self.create_qr_code(str(imei))
            img = self.draw_qr_code_text(qr, text=f"IMEI #: {imei}")
            img.save(f"{imei}.png")

    def create_qr_code(self, imei_number: str) -> qrcode.QRCode:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.generate_qr_code_data(imei_number))
        qr.make_image(fill_color="black", back_color="white")
        return qr

    def draw_qr_code_text(self, qr: qrcode.QRCode, text: str) -> Image:
        img = qr.make_image(fit=True)
        img = img.convert("RGB")
        overlay = ImageDraw.Draw(img)

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf", 28
        )
        padding = 10

        text_bbox = overlay.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        img_w, img_h = img.size
        x_pos = (img_w - text_w) / 2
        y_pos = img_h - text_h - padding - 10

        overlay.text((x_pos, y_pos), text, font=font, fill="black")
        return img

    def generate_qr_code_data(self, imei_number: str) -> str:
        return urllib.parse.urljoin(
            "https://app.terminusgps.com",
            reverse("tracker:units", query={"imei": imei_number}),
        )
