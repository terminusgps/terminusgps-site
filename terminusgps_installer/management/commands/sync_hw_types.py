from django.core.management.base import BaseCommand
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.models import WialonHardwareType


class Command(BaseCommand):
    help = "Syncronizes Wialon hardware types between the installer application and Wialon."

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        with WialonSession() as session:
            hw_types_list = [
                {t.get("id"): t.get("name")} for t in wialon_utils.get_hw_types(session)
            ]
            WialonHardwareType.objects.bulk_create(
                [
                    WialonHardwareType.objects.create(
                        id=t.get("id"), name=t.get("name")
                    )
                    for t in hw_types_list
                    if t.get("id")
                    and int(t.get("id"))
                    not in list(
                        WialonHardwareType.objects.filter()
                        .values_list("id", flat=True)
                        .distinct()
                    )
                ]
            )
