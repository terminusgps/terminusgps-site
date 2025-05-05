from django.core.management.base import BaseCommand
from terminusgps.wialon.session import WialonSession

from terminusgps_install.models import WialonAccount


class Command(BaseCommand):
    help = "Retrieves Wialon accounts from the Wialon API and generates WialonAccount objects for them."

    def handle(self, *args, **options):
        with WialonSession() as session:
            response = session.wialon_api.core_search_items(
                **{
                    "spec": {
                        "itemsType": "avl_resource",
                        "propName": "sys_id,sys_name",
                        "propValueMask": "*,*",
                        "sortType": "sys_id,sys_name",
                    },
                    "force": 0,
                    "flags": 1,
                    "from": 0,
                    "to": 0,
                }
            )
            wialon_resources = {
                item.get("id"): item.get("nm") for item in response.get("items", [{}])
            }
            accounts = (
                WialonAccount.objects.create(wialon_id=id, name=name, users=None)
                for id, name in wialon_resources.items()
            )
            WialonAccount.objects.bulk_create(accounts)
