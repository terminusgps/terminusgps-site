import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Builds the sphinx documentation for terminusgps-site"

    def handle(self, *args, **kwargs):
        os.system("uv run sphinx-build -M html ./docs/source ./docs/build")
        self.stdout.write(self.style.SUCCESS("Successfully built documentation."))
