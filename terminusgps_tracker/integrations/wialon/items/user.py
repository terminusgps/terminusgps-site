from typing import TypedDict
from urllib.parse import quote_plus

import terminusgps_tracker.integrations.wialon.flags as flag
from terminusgps_tracker.integrations.wialon.items.base import WialonBase

DEFAULT_ACCESS_MASK: int = sum(
    [
        flag.ACCESSFLAG_VIEW_ITEM_BASIC,
        flag.ACCESSFLAG_VIEW_ITEM_DETAILED,
        flag.ACCESSFLAG_RENAME_ITEM,
        flag.ACCESSFLAG_VIEW_CUSTOM_FIELDS,
        flag.ACCESSFLAG_MANAGE_CUSTOM_FIELDS,
        flag.ACCESSFLAG_MANAGE_ICON,
        flag.ACCESSFLAG_QUERY_REPORTS,
        flag.ACCESSFLAG_VIEW_ATTACHED_FILES,
        flag.ACCESSFLAG_UNIT_VIEW_CONNECTIVITY,
        flag.ACCESSFLAG_UNIT_VIEW_SERVICE_INTERVALS,
        flag.ACCESSFLAG_UNIT_IMPORT_MESSAGES,
        flag.ACCESSFLAG_UNIT_EXPORT_MESSAGES,
        flag.ACCESSFLAG_UNIT_VIEW_COMMANDS,
    ]
)


class CreateWialonUserKwargs(TypedDict):
    owner_id: int
    name: str
    password: str


class WialonUser(WialonBase):
    def create(self, **kwargs: CreateWialonUserKwargs) -> str | None:
        owner_id: int = kwargs["owner_id"]
        name: str = kwargs["name"]
        password: str = kwargs["password"]

        response: dict = self.session.wialon_api.core_create_user(
            **{
                "creatorId": str(owner_id),
                "name": name,
                "password": password,
                "dataFlags": flag.DATAFLAG_USER_BASE,
            }
        )
        return response.get("item", {}).get("id")

    def _get_access_response(self, hw_type: str) -> dict:
        return self.session.wialon_api.user_get_items_access(
            **{
                "userId": self.id,
                "directAccess": True,
                "itemSuperclass": hw_type,
                "flags": 0x2,
            }
        )

    @property
    def units(self) -> list[str]:
        response = self._get_access_response(hw_type="avl_unit")
        return [key for key in response.keys()]

    @property
    def groups(self) -> list[str]:
        response = self._get_access_response(hw_type="avl_unit_group")
        return [key for key in response.keys()]

    def has_access(self, other_item: WialonBase) -> bool:
        response = self._get_access_response(hw_type=other_item.hw_type)
        items = [key for key in response.keys()]
        if str(other_item.id) in items:
            return True
        return False

    def assign_phone(self, phone: str) -> None:
        self.add_cproperty(("phone", quote_plus(phone)))

    def assign_email(self, email: str) -> None:
        self.add_cproperty(("email", email))

    def assign_item(
        self, item: WialonBase, access_mask: int = DEFAULT_ACCESS_MASK
    ) -> None:
        """Assigns an item to this user according to the supplied access mask integer."""
        self.session.wialon_api.user_update_item_access(
            **{"userId": self.id, "itemId": item.id, "accessMask": access_mask}
        )

    def set_settings_flags(self, flags: int, flags_mask: int) -> None:
        self.session.wialon_api.user_update_user_flags(
            **{"userId": self.id, "flags": flags, "flagsMask": flags_mask}
        )

    def update_password(self, old_password: str, new_password: str) -> None:
        self.session.wialon_api.user_update_password(
            **{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            }
        )
