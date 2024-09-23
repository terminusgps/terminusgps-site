from typing import Optional

from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.session import WialonSession

class WialonBase:
    def __init__(self, *, id: Optional[str] = None, session: WialonSession, **kwargs) -> None:
        self._id = id
        self._session = session
        if self._id is None:
            self.create(**kwargs)
        self.populate()

    def __str__(self) -> str:
        return f"{self.__class__}:{self.id}"

    @property
    def session(self) -> WialonSession:
        return self._session

    @property
    def id(self) -> int | None:
        return int(self._id) if self._id else None

    def create(self, **kwargs) -> None:
        """Creates a Wialon object and sets this instance's id attribute to the Wialon object's id."""
        raise NotImplementedError("Subclasses must implement this method.")

    def populate(self) -> None:
        """Retrieves and sets hw_type and name for this Wialon object."""
        try:
            response = self.session.wialon_api.core_search_item(**{
                "id": self.id,
                "flags": flag.DATAFLAG_UNIT_BASE,
            })
        except WialonError as e:
            raise e
        else:
            item = response.get("item", {})
            self.hw_type = item.get("cls", None)
            self.name = item.get("nm", None)

    def rename(self, new_name: str) -> None:
        try:
            self.session.wialon_api.item_update_name(**{
                "itemId": self.id,
                "name": new_name,
            })
        except WialonError as e:
            raise e
        else:
            self.populate()

    def add_afield(self, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_admin_field(**{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            })
        except WialonError as e:
            raise e

    def update_afield(self, field_id: int, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_admin_field(**{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            })
        except WialonError as e:
            raise e

    def add_cfield(self, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_custom_field(**{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            })
        except WialonError as e:
            raise e

    def update_cfield(self, field_id: int, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_custom_field(**{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            })
        except WialonError as e:
            raise e

    def add_cproperty(self, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_custom_property(**{
                "itemId": self.id,
                "name": field[0],
                "value": field[1],
            })
        except WialonError as e:
            raise e

    def add_profile_field(self, field: tuple[str, str]) -> None:
        try:
            self.session.wialon_api.item_update_profile_field(**{
                "itemId": self.id,
                "n": field[0],
                "v": field[1],
            })
        except WialonError as e:
            raise e

    def get_bound_account_id(self) -> str:
        try:
            response = self.session.wialon_api.account_list_change_accounts(**{
                "units": [self.id]
            })
        except WialonError as e:
            raise e
        else:
            return response[0].get("id", "")
