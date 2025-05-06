import argparse

import boto3
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Uploads a pair of templates to `AWS SES <https://docs.aws.amazon.com/ses/>`_"
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
        parser.add_argument("subject", type=str)
        parser.add_argument("text_file", type=argparse.FileType("r"))
        parser.add_argument("html_file", type=argparse.FileType("r"))
        parser.add_argument("region", nargs="?", type=str, default="us-east-1")

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        ses_client = boto3.Session().client("ses", region_name=options["region"])
        ses_client.create_template(
            **{
                "Template": {
                    "TemplateName": options["name"],
                    "SubjectPart": options["subject"],
                    "TextPart": options["text_file"].read(),
                    "HtmlPart": options["html_file"].read(),
                }
            }
        )
