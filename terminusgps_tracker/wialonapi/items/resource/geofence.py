
from wialon.api import WialonError

from terminusgps_tracker.wialonapi.items.base import WialonBase

class WialonGeofence(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("resource", None) is None:
            raise ValueError("Tried to create a geofence but resource was none.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create a geofence but name was none.")
        if kwargs.get("coords", None) is None:
            raise ValueError("Tried to create a geofence but coords were none.")

        try:
            response = self.session.wialon_api.resource_update_zone(**{
                "itemId": kwargs["resource"].id,
                "id": 0,
                "callMode": "create",
                "n": kwargs["name"],
                "d": kwargs["name"],
                "t": 3,
                "w": 2,
                "f": 1,
                "c": int("08ff00", 16),
                "tc": int("030303", 16),
                "ts": 12,
                "min": 1,
                "max": 19,
                "path": "",
                "libId": 0,
                "p": {
                    "x": kwargs["coords"][0],
                    "y": kwargs["coords"][1],
                    "r": kwargs["coords"][2],
                },
            })
        except WialonError as e:
            raise e
        else:
            self._id: str = str(response[0])
