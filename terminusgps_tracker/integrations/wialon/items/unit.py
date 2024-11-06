from typing import Any, TypedDict
from urllib.parse import quote_plus

import terminusgps_tracker.integrations.wialon.flags as flag
from terminusgps_tracker.integrations.wialon.items.base import WialonBase


class CreateWialonUnitKwargs(TypedDict):
    owner: WialonBase
    name: str
    hw_type: str


class WialonUnit(WialonBase):
    def create(self, **kwargs: CreateWialonUnitKwargs) -> str | None:
        owner: WialonBase = kwargs["owner"]
        name: str = kwargs["name"]
        hw_type: str = kwargs["hw_type"]

        response: dict = self.session.wialon_api.core_create_unit(
            **{
                "creatorId": str(owner.id),
                "name": name,
                "hwTypeId": hw_type,
                "dataFlags": flag.DATAFLAG_UNIT_BASE,
            }
        )
        return response.get("item", {}).get("id")

    def populate(self) -> None:
        super().populate()
        search = self.session.wialon_api.core_search_item(
            id=self.id, flags=flag.DATAFLAG_UNIT_ADVANCED_PROPERTIES
        )
        self.uid = search.get("uid", "")
        self.phone = search.get("ph", "")
        self.is_active = bool(search.get("act", 0))

    def set_access_password(self, access_password: str) -> None:
        self.session.wialon_api.unit_update_access_password(
            **{"itemId": self.id, "accessPassword": access_password}
        )

    def activate(self) -> None:
        if self.is_active:
            return
        else:
            self.session.wialon_api.unit_set_active(
                **{"itemId": self.id, "active": int(True)}
            )
            self.populate()

    def deactivate(self) -> None:
        if not self.is_active:
            return
        else:
            self.session.wialon_api.unit_set_active(
                **{"itemId": self.id, "active": int(False)}
            )
            self.populate()

    def assign_phone(self, phone: str) -> None:
        self.session.wialon_api.unit_update_phone(
            **{"itemId": self.id, "phoneNumber": quote_plus(phone)}
        )
        self.populate()

    def _get_fields(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        result = self.session.wialon_api.core_search_item(
            id=self.id,
            flags=sum(
                [flag.DATAFLAG_UNIT_CUSTOM_FIELDS, flag.DATAFLAG_UNIT_ADMIN_FIELDS]
            ),
        )
        return result["item"]["aflds"].values(), result["item"]["flds"].values()

    def get_phone_numbers(self) -> list[str]:
        phone_numbers = []
        admin_fields, custom_fields = self._get_fields()
        if self.phone:
            phone_numbers.append(self.phone)
        for field in admin_fields + custom_fields:
            if field.get("n") == "to_number":
                phone_numbers.append(field.get("v"))
        return phone_numbers
