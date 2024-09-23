from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.items.unit_group import WialonUnitGroup


class WialonUnit(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create unit but creator id was not provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create unit but name was not provided.")
        if kwargs.get("hw_type", None) is None:
            raise ValueError("Tried to create unit but hw_type was not provided.")

        try:
            response = self.session.wialon_api.core_create_unit(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "hwTypeId": kwargs["hw_type"],
                "dataFlags": flag.DATAFLAG_UNIT_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")

    def populate(self) -> None:
        super().populate()
        try:
            search_result = self.session.wialon_api.core_search_item(**{
                "id": self.id,
                "flags": flag.DATAFLAG_UNIT_ADVANCED_PROPERTIES,
            })
        except WialonError as e:
            raise e
        else:
            self.unique_id = search_result.get("uid", "")
            self.phone = search_result.get("ph", "")
            self.is_active = bool(search_result.get("act", 0))

    def is_member(self, group: WialonUnitGroup) -> bool:
        if self.id in group.units:
            return True
        else:
            return False
