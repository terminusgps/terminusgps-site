from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase


class WialonRoute(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create route but creator id was not provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create route but name was not provided.")

        try:
            response = self.session.wialon_api.core_create_route(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "dataFlags": flag.DATAFLAG_ROUTE_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")
