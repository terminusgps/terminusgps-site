from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.items.unit_group import WialonUnitGroup
from terminusgps_tracker.wialonapi.items.resource import WialonResource


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

    def is_member(self, group: WialonUnitGroup) -> bool:
        if self.id in group.units:
            return True
        else:
            return False

    def migrate(self, resource: WialonResource) -> None:
        try:
            self.session.wialon_api.account_change_account(**{
                "itemId": self.id,
                "resourceId": resource.id,
            })
        except WialonError as e:
            raise e
