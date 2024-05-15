from wialon import Wialon
from wialon import flags as wialon_flag
from typing import Self, Optional, Union
from django.conf import settings


class WialonSession:
    def __init__(self) -> None:
        self.wialon_api = Wialon()
        self._token = settings.WIALON_API_ACCESS_TOKEN

        if self._token is None:
            raise ValueError("WIALON_API_ACCESS_TOKEN env variable is not set")

        return None

    def __enter__(self) -> Self:
        login = self.wialon_api.token_login(token=self._token)
        self.wialon_api.sid = login["eid"]
        self._sid = login["eid"]

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Union[str, None]:
        self.wialon_api.core_logout()

        __err = f"{exc_type = }, {exc_val = }, {exc_tb = }"
        if exc_type is not None:
            return __err

        return None

    @property
    def sid(self) -> Union[str, None]:
        return self._sid


class WialonUnit:
    def __init__(
        self,
        session: WialonSession,
        imei: Union[str, None] = None,
        id: Union[int, None] = None,
    ) -> None:

        self.session = session.wialon_api
        if (imei is None and id is None) or (imei is not None and id is not None):
            raise ValueError("Either imei or id must be provided, but not both")

        if imei:
            self._imei = imei
            self._id = self._get_id(imei)

        if id:
            self._id = id
            self._imei = self._get_imei(id)

        return None

    def __str__(self) -> str:
        return f"{self._imei}"

    @property
    def imei(self) -> Union[str, None]:
        return self._imei

    @property
    def id(self) -> int:
        return self._id

    def _get_info(self, flags: int) -> Union[dict, None]:
        params = {
            "id": self._id,
            "flags": flags,
        }
        return self.session.core_search_item(**params).get("item")

    def _get_imei(self, id: int) -> Union[str, None]:
        if (id is None) and (self._id is None):
            raise ValueError("id is not set")

        self._id = id
        flags = wialon_flag.ITEM_UNIT_DATAFLAG_RESTRICTED

        return self._get_info(flags).get("uid")

    def _get_id(self, imei: str) -> int:
        print("Running WialonUnit._get_id")
        params = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"*{imei}*",
                "sortType": "sys_unique_id",
            },
            "force": 1,
            "flags": wialon_flag.ITEM_DATAFLAG_BASE,
            "from": 0,
            "to": 0,
        }
        response = self.session.core_search_items(**params)
        id = response.get("items")[0].get("id")
        return id
