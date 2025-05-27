from django.core.management.base import BaseCommand
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.models import WialonAccount


class Command(BaseCommand):
    help = "Syncronizes Wialon accounts between the installer application and Wialon."

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        with WialonSession() as session:
            account_list = wialon_utils.get_resources(session)
            WialonAccount.objects.bulk_create(
                [
                    WialonAccount.objects.create(id=a.id, name=a.name)
                    for a in account_list
                    if a.is_account
                    and int(a.id)
                    not in list(
                        WialonAccount.objects.filter()
                        .values_list("id", flat=True)
                        .distinct()
                    )
                ]
            )
