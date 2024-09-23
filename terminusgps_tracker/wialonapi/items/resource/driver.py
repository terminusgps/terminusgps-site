from wialon.api import WialonError

from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.items.unit import WialonUnit

class WialonDriver(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("resource", None) is None:
            raise ValueError("Tried to create a driver but resource was none.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create a driver but name was none.")

        try:
            response = self.session.wialon_api.resource_update_driver(**{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": kwargs["name"],
                "f": 1,
                "pwd": "1234",
            })
        except WialonError as e:
            raise e
        else:
            self._id = str(response[0])

    def bind_unit(self, unit: WialonUnit) -> None:
        account_id: str | None = unit.get_bound_account_id()
        if account_id:
            try:
                self.session.wialon_api.resource_bind_unit_driver(**{
                    "resourceId": account_id,
                    "unitId": unit.id,
                    "driverId": self.id,
                    "time": 0,
                    "mode": 1,
                })
            except WialonError as e:
                raise e

    def unbind_unit(self, unit: WialonUnit) -> None:
        account_id: str | None = unit.get_bound_account_id()
        if account_id:
            try:
                self.session.wialon_api.resource_bind_unit_driver(**{
                    "resourceId": unit.get_bound_account_id(),
                    "unitId": unit.id,
                    "driverId": self.id,
                    "time": 0,
                    "mode": 0,
                })
            except WialonError as e:
                raise e
