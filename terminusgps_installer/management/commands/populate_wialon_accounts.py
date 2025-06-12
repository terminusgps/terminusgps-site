from django.core.management.base import BaseCommand
from terminusgps.wialon import utils
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.models import WialonAccount


class Command(BaseCommand):
    help = "Syncs Wialon accounts with the installer application"

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        with WialonSession() as session:
            resources = utils.get_resources(session)
            if resources:
                accounts = [
                    WialonAccount(id=r.id, name=r.name, uid=r.creator_id)
                    for r in resources
                    if r.is_account
                ]
                WialonAccount.objects.bulk_create(
                    accounts, ignore_conflicts=True
                )
