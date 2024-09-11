import os

from typing import Self, Optional
from wialon import Wialon, WialonError
import terminusgps_tracker.wialonapi.flags as flag

BOT_ID = "27881459"

class WialonSession:
    def __init__(self) -> None:
        self.creator_id: str = BOT_ID
        self.wialon_api: Wialon = Wialon()
        self.token: str | None = os.getenv("WIALON_HOSTING_API_TOKEN")

    def __enter__(self) -> Self:
        if self.token is None:
            raise ValueError("No Wialon API token provided.")
        result = self.wialon_api.token_login(**{
            "token": self.token,
        })
        self.wialon_api.sid = result["eid"]
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None) -> str | None:
        if any([exc_type, exc_val, exc_tb]):
            return f"Error: {exc_val}"
        self.wialon_api.core_logout()

    def set_user_access_flags(self, unit_id: str, user_id: str, flags: Optional[int] = None) -> None:
        if flags is None:
            print(f"Setting user #{user_id} to default access for item #{unit_id}...")
            flags = sum([
                flag.ACCESSFLAG_MANAGE_ATTACHED_FILES,
                flag.ACCESSFLAG_MANAGE_CUSTOM_FIELDS,
                flag.ACCESSFLAG_MANAGE_ICON,
                flag.ACCESSFLAG_MANAGE_ITEM_ACCESS,
                flag.ACCESSFLAG_QUERY_REPORTS,
                flag.ACCESSFLAG_RENAME_ITEM,
                flag.ACCESSFLAG_UNIT_EXECUTE_COMMANDS,
                flag.ACCESSFLAG_UNIT_EXPORT_MESSAGES,
                flag.ACCESSFLAG_UNIT_IMPORT_MESSAGES,
                flag.ACCESSFLAG_UNIT_MANAGE_ASSIGNMENTS,
                flag.ACCESSFLAG_UNIT_MANAGE_SERVICE_INTERVALS,
                flag.ACCESSFLAG_UNIT_MANAGE_TRIP_DETECTOR,
                flag.ACCESSFLAG_UNIT_REGISTER_EVENTS,
                flag.ACCESSFLAG_UNIT_VIEW_COMMANDS,
                flag.ACCESSFLAG_UNIT_VIEW_SERVICE_INTERVALS,
                flag.ACCESSFLAG_VIEW_ADMIN_FIELDS,
                flag.ACCESSFLAG_VIEW_ATTACHED_FILES,
                flag.ACCESSFLAG_VIEW_CUSTOM_FIELDS,
                flag.ACCESSFLAG_VIEW_ITEM_BASIC,
                flag.ACCESSFLAG_VIEW_ITEM_DETAILED,
            ])

        try:
            self.wialon_api.user_update_item_access(**{
                "userId": user_id,
                "itemId": unit_id,
                "accessMask": flags,
            })
        except WialonError as e:
            raise e
        else:
            return

    def set_user_settings_flags(self, user_id: str, flags: Optional[int] = None, flags_mask: Optional[int] = None) -> None:
        if flags is None or flags_mask is None:
            print(f"Setting user #{user_id} to default settings...")
            flags_mask = sum([
                flag.SETTINGSFLAG_USER_DISABLED,
                flag.SETTINGSFLAG_USER_CANNOT_CHANGE_PASSWORD,
                flag.SETTINGSFLAG_USER_CAN_CREATE_ITEMS,
                flag.SETTINGSFLAG_USER_CANNOT_CHANGE_SETTINGS,
                flag.SETTINGSFLAG_USER_CAN_SEND_SMS,
            ])

            flags = sum([
                -flag.SETTINGSFLAG_USER_DISABLED,
                -flag.SETTINGSFLAG_USER_CANNOT_CHANGE_PASSWORD,
                flag.SETTINGSFLAG_USER_CAN_CREATE_ITEMS,
                flag.SETTINGSFLAG_USER_CANNOT_CHANGE_SETTINGS,
                flag.SETTINGSFLAG_USER_CAN_SEND_SMS,
            ])

        try:
            self.wialon_api.user_update_user_flags(**{
                "userId": user_id,
                "flags": flags,
                "flagsMask": flags_mask,
            })
        except WialonError as e:
            raise e
        else:
            return

    def create_account(self, resource_id: str, plan: str) -> None:
        print(f"Creating account for resource #{resource_id}...")
        try:
            self.wialon_api.account_create_account(**{
                "itemId": resource_id,
                "plan": plan,
            })
        except WialonError as e:
            raise e
        else:
            return

    def create_group(self, name: str) -> str:
        print(f"Creating group '{name}'...")
        try:
            response = self.wialon_api.core_create_unit_group(**{
                "creatorId": self.creator_id,
                "name": name,
                "dataFlags": flag.DATAFLAG_UNIT_BASE,
            })
        except WialonError as e:
            raise e
        else:
            return response["item"].get("id", "")

    def create_resource(self, name: str) -> str:
        print(f"Creating resource '{name}'...")
        try:
            response = self.wialon_api.core_create_resource(**{
                "creatorId": self.creator_id,
                "name": name,
                "dataFlags": flag.DATAFLAG_RESOURCE_BASE,
            })
        except WialonError as e:
            raise e
        else:
            return response["item"].get("id", "")

    def create_user(self, username: str, password: str) -> str:
        print(f"Creating user '{username}'...")
        try:
            response = self.wialon_api.core_create_user(**{
                "creatorId": self.creator_id,
                "name": username,
                "password": password,
                "dataFlags": flag.DATAFLAG_USER_BASE,
            })
        except WialonError as e:
            raise e
        else:
            return response["item"].get("id", "")

    def get_unactivated_units(self, group_id: str = "27890571") -> list[str]:
        try:
            response = self.wialon_api.core_search_item(**{
                "id": group_id,
                "flags": flag.DATAFLAG_UNIT_BASE,
            })
        except WialonError as e:
            raise e
        else:
            return response["item"].get("u", [])

    def get_id(self, imei_number: str) -> str:
        print(f"Retrieving id from '{imei_number}'...")
        """Takes a Wialon IMEI # and returns its corresponding Wialon ID."""
        params = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"*{imei_number}*",
                "sortType": "sys_unique_id",
                "propType": "property",
                "or_logic": 0,
            },
            "force": 0,
            "flags": flag.DATAFLAG_UNIT_BASE,
            "from": 0,
            "to": 0,
        }
        try:
            items: list = self.wialon_api.core_search_items(**params).get("items", [])
        except WialonError as e:
            raise e
        else:
            if len(items) != 1:
                raise ValueError(f"Invalid IMEI #: '{imei_number}'")
            return items[0].get("id")
