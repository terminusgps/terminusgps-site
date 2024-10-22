from typing import Optional

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.session import WialonSession


class WialonBase:
    def __init__(
        self, *, id: Optional[str] = None, session: WialonSession, **kwargs
    ) -> None:
        self._session = session

        if id is None:
            self._id = self.create(**kwargs)
        else:
            self._id = id
        self.populate()

    def __str__(self) -> str:
        return f"{self.__class__}:{self.id}"

    @property
    def session(self) -> WialonSession:
        return self._session

    @property
    def id(self) -> int | None:
        return int(self._id) if self._id else None

    @property
    def bound_account_id(self) -> int:
        response = self.session.wialon_api.account_list_change_accounts(
            **{"units": [self.id]}
        )
        return int(response[0].get("id", ""))

    def has_access(self, other_item: "WialonBase") -> bool:
        response = self.session.wialon_api.core_check_accessors(
            **{"items": [other_item.id], "flags": False}
        )
        if self.id in response.keys():
            return True
        return False

    def create(self) -> str | None:
        """Creates a Wialon object and returns the newly created Wialon object's id."""
        raise NotImplementedError("Subclasses must implement this method.")

    def populate(self) -> None:
        """Retrieves and sets hw_type and name for this Wialon object."""
        item = self.session.wialon_api.core_search_item(
            **{"id": self.id, "flags": flag.DATAFLAG_UNIT_BASE}
        ).get("item", {})
        self.hw_type = item.get("cls", None)
        self.name = item.get("nm", None)
        self.uid = item.get("uid", None)

    def rename(self, new_name: str) -> None:
        self.session.wialon_api.item_update_name(
            **{"itemId": self.id, "name": new_name}
        )
        self.populate()

    def add_afield(self, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_admin_field(
            **{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            }
        )

    def update_afield(self, field_id: int, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_admin_field(
            **{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            }
        )

    def add_cfield(self, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_custom_field(
            **{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            }
        )

    def update_cfield(self, field_id: int, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_custom_field(
            **{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            }
        )

    def add_cproperty(self, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_custom_property(
            **{"itemId": self.id, "name": field[0], "value": field[1]}
        )

    def add_profile_field(self, field: tuple[str, str]) -> None:
        self.session.wialon_api.item_update_profile_field(
            **{"itemId": self.id, "n": field[0], "v": field[1]}
        )

    def delete(self) -> None:
        self.session.wialon_api.item_delete_item(**{"itemId": self.id})
