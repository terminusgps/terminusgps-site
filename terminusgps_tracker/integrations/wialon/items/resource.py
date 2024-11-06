from typing import TypedDict

import terminusgps_tracker.integrations.wialon.flags as flag
from terminusgps_tracker.integrations.wialon.items.base import WialonBase
from terminusgps_tracker.integrations.wialon.items.unit_group import WialonUnitGroup


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

    def create_notification(
        self,
        method: str,
        name: str,
        body: str,
        group: WialonUnitGroup,
        phones: list[str] | None = None,
    ) -> str | None:
        valid_methods = ["sms", "call", "phone"]
        if phones and method in valid_methods:
            text = f"to_number={",".join(phones)}&message=" + body
            target_url = f"https://api.terminusgps.com/v2/notify/{method}"
            response = self.session.wialon_api.resource_create_notification(
                **{
                    "itemId": self.id,
                    "id": 0,
                    "callMode": "create",
                    "n": name,
                    "text": text,
                    "act": [{"t": "push_messages", "p": {"url": target_url, "get": 0}}],
                    "la": "en",
                    "un": group.items,
                }
            )
            return response[0].get("id")
