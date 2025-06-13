from django.core.management.base import BaseCommand
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession


class Command(BaseCommand):
    help = "Syncs Wialon accounts with the installer application"

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided options.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        with WialonSession() as session:
            resources = session.wialon_api.core_search_item(
                **{
                    "spec": {
                        "itemsType": "avl_resource",
                        "propName": "rel_is_account",
                        "propValueMask": 1,
                        "sortType": "rel_is_account",
                        "propType": "list",
                    },
                    "force": 0,
                    "flags": (
                        flags.DataFlag.RESOURCE_BILLING_PROPERTIES
                        | flags.DataFlag.UNIT_BASE
                    ).value,
                    "from": 0,
                    "to": 0,
                }
            )
            print(f"{resources = }")
