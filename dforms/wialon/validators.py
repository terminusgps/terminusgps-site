from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .session import WialonSession


def imei_number_exists_in_db(value: str) -> str:
    params: dict = {
        "spec": {
            "itemsType": "avl_unit",
            "propName": "sys_unique_id",
            "propValueMask": value,
            "sortType": "sys_unique_id",
        },
        "force": 0,
        "flags": 1,
        "from": 0,
        "to": 0,
    }
    with WialonSession() as session:
        response = session.wialon_api.core_search_items(**params)
        total_items: int = response.get("totalItemsCount")

        if total_items != 1:
            raise ValidationError(
                _(
                    f"IMEI number `%(value)s` does not exist in the TerminusGPS database."
                ),
                params={"value": value},
                code="imei_number_does_not_exist_in_db",
            )

    return value


def imei_number_is_unassigned(value: str) -> str:
    def get_id(value: str, session: WialonSession) -> str:
        params: dict = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": value,
                "sortType": "sys_unique_id",
            },
            "force": 0,
            "flags": 1,
            "from": 0,
            "to": 0,
        }
        response = session.wialon_api.core_search_items(**params)
        unit_id: str = response.get("items")[0].get("id")

        return unit_id

    with WialonSession() as session:
        params = {
            "id": "27890571",  # Unassigned inventory group
            "flags": 1,
        }
        response = session.wialon_api.core_search_item(**params)
        unassigned_units: list[str] = response.get("item").get("u", [])
        unit_id: str = get_id(value, session)

        if unit_id not in unassigned_units:
            raise ValidationError(
                _("IMEI number `%(value)s` is already assigned to an asset."),
                code="imei_number_is_already_assigned",
                params={"value": value},
            )

    return value
