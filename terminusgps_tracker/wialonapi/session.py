import os
import logging
import string
import secrets
from typing import Self

from wialon import Wialon
from wialon import flags as wialon_flag

stdout_handler = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, handlers=[stdout_handler])
logger = logging.getLogger(__name__)


class WialonSession:
    def __init__(self, token: str = "") -> None:
        self.wialon_api: Wialon = Wialon()
        self.token: str = (
            token if token else os.environ.get("WIALON_HOSTING_API_TOKEN", "")
        )

        return None

    def __enter__(self) -> Self:
        login = self.wialon_api.token_login(token=self.token)
        self.wialon_api.sid = login["eid"]
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None) -> str | None:
        if any([exc_type, exc_val, exc_tb]):
            return f"Error: {exc_val}"
        self.wialon_api.core_logout()
        return None

    def create_wialon_user(self, username: str, password: str) -> str | None:
        """Creates a Wialon user and returns its ID."""
        logger.info(f"Creating a new Wialon user named '{username}'...")
        params = {
            "creatorId": "27881459", # Terminus1000's User ID
            "name": username,
            "password": password,
            "dataFlags": wialon_flag.ITEM_DATAFLAG_BASE,
        }
        logger.debug(f"WialonSession.create_wialon_user: {params}")
        response = self.wialon_api.core_create_user(**params)
        logger.debug(f"WialonSession.create_wialon_user: {response}")
        return response.get("item", {}).get("id", None)

    def assign_wialon_asset(self, user_id: str, asset_name: str, imei_number: str) -> str | None:
        """Assigns a Wialon asset to the provided user ID, returns its own ID."""
        asset_id = self._get_wialon_id(imei_number)
        self.rename_wialon_asset(asset_id, asset_name)
        self.set_default_wialon_access(user_id, asset_id)

    def set_user_settings_flags(self, user_id: str) -> None:
        """Sets user settings flags on the provided Wialon user."""
        logger.info(f"Setting default userflags for user #{user_id}.")
        params = {
            "userId": user_id,
            "flags": sum([
                wialon_flag.ITEM_USER_USERFLAG_CANNOT_CHANGE_SETTINGS,
                wialon_flag.ITEM_USER_USERFLAG_CANNOT_CHANGE_PASSWORD,
            ]),
            "flagsMask": wialon_flag.ITEM_USER_USERFLAG_CANNOT_CHANGE_SETTINGS - wialon_flag.ITEM_USER_USERFLAG_CANNOT_CHANGE_PASSWORD,
        }
        logger.debug(f"WialonSession.set_user_settings_flags params: {params}")
        response = self.wialon_api.user_update_user_flags(**params)
        logger.debug(f"WialonSession.set_user_settings_flags params: {response}")



    def set_default_wialon_access(self, user_id: str, asset_id: str) -> None:
        """Sets the default access flags for the provided Wialon asset and user."""
        logger.info(f"Setting default access flags for user #{user_id} and asset #{asset_id}.")
        params = {
            "userId": user_id,
            "itemId": asset_id,
            "accessMask": sum([
                wialon_flag.ITEM_ACCESSFLAG_VIEW,
                wialon_flag.ITEM_ACCESSFLAG_VIEW_PROPERTIES,
                wialon_flag.ITEM_ACCESSFLAG_EDIT_NAME,
                wialon_flag.ITEM_ACCESSFLAG_VIEW_CFIELDS,
                wialon_flag.ITEM_ACCESSFLAG_EDIT_CFIELDS,
                wialon_flag.ITEM_ACCESSFLAG_EDIT_IMAGE,
                wialon_flag.ITEM_ACCESSFLAG_VIEW_ADMINFIELDS,
            ])
        }
        logger.debug(f"WialonSession.set_default_wialon_access: {params}")
        response = self.wialon_api.user_update_item_access(**params)
        logger.debug(f"WialonSession.set_default_wialon_access response: {response}")

    def rename_wialon_asset(self, wialon_id: str, name: str) -> None:
        """Renames a given Wialon asset to the provided name."""
        logger.info(f"Renaming Wialon id '{wialon_id}' to '{name}'...")
        if len(name) <= 3:
            raise ValueError(f"New name must be at least 4 characters long. '{name}' is {len(name)} chars long.")
        params = {
            "itemId": wialon_id,
            "name": name,
        }
        logger.debug(f"WialonSession.rename_wialon_asset params: {params}")
        response = self.wialon_api.item_update_name(**params)
        logger.debug(f"WialonSession.rename_wialon_asset response: {response}")

    def _get_wialon_id(self, imei_number: str) -> str:
        """Takes a Wialon IMEI # and returns its corresponding Wialon ID."""
        logger.info(f"Retrieving Wialon id for '{imei_number}'...")
        params = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"*{imei_number}*",
                "sortType": "sys_unique_id",
                "propType": "property",
                "or_logic": 1,
            },
            "force": 0,
            "flags": wialon_flag.ITEM_DATAFLAG_BASE,
            "from": 0,
            "to": 0,
        }
        logger.debug(f"WialonSession._get_wialon_id params: {params}")
        response = self.wialon_api.core_search_items(**params)
        logger.debug(f"WialonSession._get_wialon_id response: {response}")
        if not response.get("totalItemsCount", 0) == 1:
            raise ValueError(f"IMEI number '{imei_number}' not found in Wialon.")
        return response.get("items")[0].get("id")

    def generate_wialon_password(self, length: int = 12) -> str:
        """Returns a valid Wialon password of the given length."""
        length += 1
        letters = tuple(string.ascii_letters)
        numbers = tuple(string.digits)
        symbols = ("@", "#", "$", "%", "!")

        while True:
            password = "".join(
                secrets.choice(letters + numbers + symbols) for i in range(length)
            )
            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in symbols for c in password)
            ):
                break
        return password
