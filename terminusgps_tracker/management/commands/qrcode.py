import argparse

import qrcode
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates QR code images for Wialon units by IMEI #."

    @property
    def domain(self) -> str:
        return "app.terminusgps.com"

    @property
    def protocol(self) -> str:
        return "https"

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
            self.generate_qr_code(str(imei))

    def generate_qr_code(self, imei_number: str) -> None:
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=10, border=4
        )
        qr.add_data(
            f"{self.protocol}://{self.domain}/assets/create/?imei={imei_number}"
        )
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"{imei_number}.png")
