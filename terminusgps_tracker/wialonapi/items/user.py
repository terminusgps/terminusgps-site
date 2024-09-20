from wialon.api import WialonError

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
    flag.ACCESSFLAG_VIEW_ADMIN_FIELDS,
    flag.ACCESSFLAG_VIEW_ATTACHED_FILES,
    flag.ACCESSFLAG_UNIT_VIEW_CONNECTIVITY,
    flag.ACCESSFLAG_UNIT_VIEW_SERVICE_INTERVALS,
    flag.ACCESSFLAG_UNIT_IMPORT_MESSAGES,
    flag.ACCESSFLAG_UNIT_EXPORT_MESSAGES,
    flag.ACCESSFLAG_UNIT_VIEW_COMMANDS,
])

class WialonUser(WialonBase):
    def create(self, **kwargs) -> None:
        """Creates a new user in Wialon and sets this user's id attribute to the newly created user's Wialon id."""
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create user but creator id was not provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create user but name was not provided.")
        if kwargs.get("password", None) is None:
            raise ValueError("Tried to create user but password was not provided.")

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
            self.session.wialon_api.item_update_custom_property(**{
                "itemId": self.id,
                "name": "phone",
                "value": phone,
            })
        except WialonError as e:
            raise e

    def assign_email(self, email: str) -> None:
        """Sets the email for this user in Wialon."""
        try:
            self.session.wialon_api.item_update_custom_property(**{
                "itemId": self.id,
                "name": "email",
                "value": email,
            })
        except WialonError as e:
            raise e

    def assign_unit(self, unit: WialonBase, access_mask: int = DEFAULT_ACCESS_MASK) -> None:
        """Assigns a WialonUnit to this user according to a supplied access mask integer."""
        try:
            self.session.wialon_api.user_update_item_access(**{
                "userId": self.id,
                "itemId": unit.id,
                "accessMask": access_mask
            })
        except WialonError as e:
            raise e

    def set_settings_flags(self, flags: int, flags_mask: int) -> None:
        """Sets the settings flags for this user according to supplied flags and flag mask integers."""
        try:
            self.session.wialon_api.user_update_user_flags(**{
                "userId": self.id,
                "flags": flags,
                "flagsMask": flags_mask,
            })
        except WialonError as e:
            raise e

    def update_password(self, old_password: str, new_password: str) -> None:
        """Updates the password of this user to the supplied new password."""
        try:
            self.session.wialon_api.user_update_password(**{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            })
        except WialonError as e:
            raise e
