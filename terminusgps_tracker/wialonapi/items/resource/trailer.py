from wialon.api import WialonError

from terminusgps_tracker.wialonapi.items.base import WialonBase

class WialonTrailer(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("resource", None) is None:
            raise ValueError("Tried to create a trailer but resource was none.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create a trailer but name was none.")

        try:
            response = self.session.wialon_api.resource_update_trailer(**{
                "itemId": kwargs["resource"].id,
                "id": 0,
                "callMode": "create",
                "n": kwargs["name"],
            })
        except WialonError as e:
            raise e
        else:
            self._id = str(response[0])
