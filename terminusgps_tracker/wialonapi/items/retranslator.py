from dataclasses import dataclass

from wialon.api import WialonError

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase

@dataclass
class WialonRetranslatorConfig:
    protocol: str = "wialon_ips"
    server: str = "hst-api.wialon.com"
    port: int = 20332
    auth: str = ""
    ssl: bool = False
    debug: bool = False
    v6type: bool = False
    attach_sensors: bool = False


class WialonRetranslator(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("creator_id", None) is None:
            raise ValueError("Tried to create retranslator but creator id was not provided.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create retranslator but name was not provided.")
        if kwargs.get("config", None) is None:
            raise ValueError("Tried to create retranslator but config was not provided.")

        try:
            response = self.session.wialon_api.core_create_retranslator(**{
                "creatorId": kwargs["creator_id"],
                "name": kwargs["name"],
                "config": {
                    "protocol": kwargs["config"].protocol,
                    "server": kwargs["config"].server,
                    "port": kwargs["config"].port,
                    "auth": kwargs["config"].auth,
                    "ssl": int(kwargs["config"].ssl),
                    "debug": int(kwargs["config"].debug),
                    "v6type": int(kwargs["config"].v6type),
                    "attach_sensors": int(kwargs["config"].attach_sensors),
                },
                "dataFlags": flag.DATAFLAG_RESOURCE_BASE,
            })
        except WialonError as e:
            raise e
        else:
            self._id = response.get("item", {}).get("id")
