import json

from wialon.api import WialonError
from urllib.parse import quote_plus

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase

DEFAULT_ACCESS_MASK: int = sum([
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
])

class WialonUser(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create a user but creator id was none.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create a user but name was none.")
        if kwargs.get("password", None) is None:
            raise ValueError("Tried to create a user but password was none.")

        try:
            response = self.session.wialon_api.core_create_user(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "password": kwargs["password"],
                "dataFlags": flag.DATAFLAG_USER_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")

    def assign_phone(self, phone: str) -> None:
        """Sets the phone for this user in Wialon."""
        try:
            self.add_cproperty(("phone", quote_plus(phone)))
        except WialonError as e:
            raise e

    def assign_email(self, email: str) -> None:
        """Sets the email for this user in Wialon."""
        try:
            self.add_cproperty(("email", email))
        except WialonError as e:
            raise e

    def assign_unit(self, unit: WialonBase, access_mask: int = DEFAULT_ACCESS_MASK) -> None:
        """Assigns a `WialonUnit` to this user according to a supplied access mask integer."""
        try:
            self.session.wialon_api.user_update_item_access(**{
                "userId": self.id,
                "itemId": unit.id,
                "accessMask": access_mask
            })
        except WialonError as e:
            raise e

    def set_settings_flags(self, flags: int, flags_mask: int) -> None:
        try:
            self.session.wialon_api.user_update_user_flags(**{
                "userId": self.id,
                "flags": flags,
                "flagsMask": flags_mask,
            })
        except WialonError as e:
            raise e

    def update_password(self, old_password: str, new_password: str) -> None:
        try:
            self.session.wialon_api.user_update_password(**{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            })
        except WialonError as e:
            raise e

    def send_online_notice(self, subject: str, body: str = "") -> None:
        raise NotImplementedError
        def create_message(body: str) -> str:
            return json.dumps({
                "body": body,
                "head": {
                    "c": int("030303", 16),
                    "fs": 12,
                    "multiple": 0,
                },
            })

        try:
            self.session.wialon_api.user_update_user_notification(**{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "h": subject,
                "d": create_message(body),
                "s": "",
                "ttl": "",
            })
        except WialonError as e:
            raise e
