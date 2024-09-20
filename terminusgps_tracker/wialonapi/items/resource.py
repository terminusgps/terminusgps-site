from typing import Optional
from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase

class WialonResource(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create resource but no creator id was provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create resource but no name was provided.")

        try:
            response = self.session.wialon_api.core_create_resource(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "dataFlags": flag.DATAFLAG_RESOURCE_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")

    def create_geofence(
        self,
        name: str,
        coords: tuple[float, float],
        radius: int = 100,
        color: str = "030303",
        text_color: str = "030303",
        desc: Optional[str] = None,
    ) -> None:
        try:
            self.session.wialon_api.resource_update_zone(**{
                "itemId": self.id,
                "callMode": "create",
                "n": name,
                "d": desc if desc else name,
                "t": 3,
                "w": 2,
                "f": 0x10,
                "c": int(color, 16),
                "tc": int(text_color, 16),
                "ts": 12,
                "min": 1,
                "max": 19,
                "path": "",
                "libId": 0,
                "p": {
                    "x": coords[0],
                    "y": coords[1],
                    "r": radius,
                },
            })
        except WialonError as e:
            raise e
