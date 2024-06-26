from dataclasses import dataclass

from wialon import flags as wialon_flag

from .query import WialonQuery
from .session import WialonSession


@dataclass
class WialonUnit:
    id: str
    name: str
    imei: str
    session: WialonSession

    def __post_init__(self) -> None:
        self._groups = self._get_groups()

    def __str__(self) -> str:
        return f"{self.name} - {self.id}"

    def _get_groups(self) -> list[str]:
        query = WialonQuery(
            items_type="avl_unit",
            prop_value_mask=self.id,
            prop_name="avl_unit_group",
            sort_type="avl_id",
        )
        query.set_flags([wialon_flag.ITEM_DATAFLAG_BASE])
        result = query.execute(self.session)
        return [item["id"] for item in result.get("items", {})]

    def rename(self, new_name: str) -> None:
        params = {
            "itemId": self.id,
            "name": new_name,
        }
        self.session.wialon_api.item_update_name(**params)

    def add_custom_field(self, key: str, value: str) -> None:
        params = {
            "itemId": self.id,
            "callMode": "create",
            "n": key,
            "v": value,
        }
        self.session.wialon_api.item_update_custom_field(**params)
