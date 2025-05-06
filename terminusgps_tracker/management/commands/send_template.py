import argparse

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Sends an email via an `AWS SES <https://docs.aws.amazon.com/ses/>`_ template."
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds arguments to the command.

        :param parser: An argument parser.
        :type parser: :py:obj:`argparse.ArgumentParser`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        parser.add_argument("name", type=str)
        parser.add_argument("destination", nargs="+", type=str)
        parser.add_argument("context", nargs="+")
        parser.add_argument("region", nargs="?", type=str, default="us-east-1")

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        ses_client = boto3.Session().client("ses", region_name=options["region"])
        ses_client.send_templated_email(
            **{
                "Source": settings.DEFAULT_FROM_EMAIL,
                "Destination": {"ToAddresses": options["destination"]},
                "ReplyToAddresses": ["support@terminusgps.com"],
                "ReturnPath": "support@terminusgps.com",
            }
        )
