from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase

class WialonUnitGroup(WialonBase):
    def _get_unit_list(self) -> list:
        try:
            response = self.session.wialon_api.core_search_items(**{
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
            })
        except WialonError as e:
            raise e
        else:
            return response.get("items")[0].get("u", [])

    @property
    def units(self) -> list:
        try:
            self._units = self._get_unit_list()
        except WialonError as e:
            raise e
        else:
            return self._units

    def is_member(self, unit: WialonBase) -> bool:
        if self.units and unit.id in self.units:
            return True
        else:
            return False

    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create group but creator id was not provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create group but name was not provided.")

        try:
            response = self.session.wialon_api.core_create_unit_group(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "dataFlags": flag.DATAFLAG_UNIT_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")

    def add_unit(self, unit: WialonBase) -> None:
        """Adds a WialonUnit to this group."""
        if unit.id is None:
            raise ValueError(f"Invalid unit provided: {unit}")
        elif not self.units:
            new_units: list[str] = [str(unit.id)]
        else:
            new_units: list[str] = self.units.copy().append(str(unit.id))

        try:
            self.session.wialon_api.unit_group_update_units(**{
                "itemId": self.id,
                "units": new_units,
            })
        except WialonError as e:
            raise e

    def rm_unit(self, unit: WialonBase) -> None:
        """Removes a WialonUnit from this group, if it is a member of this group."""
        if not self.units:
            raise ValueError("Failed to retrieve this group's members.")
        elif unit.id is None:
            raise ValueError(f"Invalid unit provided: {unit}")

        if self.is_member(unit):
            target_index: int = self.units.index(str(unit.id))
            new_units: list[str] = self.units.copy().pop(target_index)
            try:
                self.session.wialon_api.unit_group_update_units(**{
                    "itemId": self.id,
                    "units": new_units,
                })
            except WialonError as e:
                raise e
