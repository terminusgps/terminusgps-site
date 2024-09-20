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
