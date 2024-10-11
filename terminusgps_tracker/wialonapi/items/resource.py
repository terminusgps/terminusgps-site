from typing import TypedDict

import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.items.base import WialonBase


class CreateWialonResourceKwargs(TypedDict):
    owner: WialonBase
    name: str


class WialonResource(WialonBase):
    def create(self, **kwargs: CreateWialonResourceKwargs) -> str | None:
        owner: WialonBase = kwargs["owner"]
        name: str = kwargs["name"]

        if len(name) < 4:
            raise ValueError(
                f"Name must be at least 4 chars long. Got {len(name)} chars."
            )

        response: dict = self.session.wialon_api.core_create_resource(
            **{
                "creatorId": owner.id,
                "name": name,
                "dataFlags": flag.DATAFLAG_RESOURCE_BASE,
                "skipCreatorCheck": 1,
            }
        )
        return response.get("item", {}).get("id")
