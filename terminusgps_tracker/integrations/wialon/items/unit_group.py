from typing import TypedDict
import terminusgps_tracker.integrations.wialon.flags as flag
from terminusgps_tracker.integrations.wialon.items.base import WialonBase

from .user import DEFAULT_ACCESS_MASK, WialonUser


class CreateWialonUnitGroupKwargs(TypedDict):
    owner: WialonBase
    name: str


class WialonUnitGroup(WialonBase):
    def create(self, **kwargs: CreateWialonUnitGroupKwargs) -> str | None:
        owner: WialonBase = kwargs["owner"]
        name: str = kwargs["name"]

        response: dict = self.session.wialon_api.core_create_unit_group(
            **{
                "creatorId": owner.id,
                "name": name,
                "dataFlags": flag.DATAFLAG_UNIT_BASE,
            }
        )
        return response.get("item", {}).get("id")

    @property
    def items(self) -> list[str]:
        response = self.session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_id",
                    "propValueMask": str(self.id),
                    "sortType": "sys_id",
                    "propType": "property",
                    "or_logic": 0,
                },
                "force": 1,
                "flags": flag.DATAFLAG_UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        )
        return [str(unit_id) for unit_id in response.get("items")[0].get("u", [])]

    def is_member(self, item: WialonBase) -> bool:
        if str(item.id) in self.items:
            return True
        return False

    def grant_access(
        self, user: WialonUser, access_mask: int = DEFAULT_ACCESS_MASK
    ) -> None:
        """Grants access to this group to the provided user."""
        self.session.wialon_api.user_update_item_access(
            **{"userId": user.id, "itemId": self.id, "accessMask": access_mask}
        )

    def add_item(self, item: WialonBase) -> None:
        """Adds a Wialon object to this group."""
        current_items = self.items
        if not current_items:
            new_items: list[str] = [str(item.id)]
        else:
            new_items: list[str] = current_items + [str(item.id)]

        self.session.wialon_api.unit_group_update_units(
            **{"itemId": self.id, "units": new_items}
        )

    def rm_item(self, item: WialonBase) -> None:
        """Removes a Wialon object from this group, if it is a member of this group."""
        if not self.is_member(item):
            raise ValueError(
                f"Cannot remove {item} because it is not a member of this group."
            )

        current_items = self.items
        new_items = [unit_id for unit_id in current_items if unit_id != str(item.id)]
        self.session.wialon_api.unit_group_update_units(
            **{"itemId": self.id, "units": new_items}
        )
