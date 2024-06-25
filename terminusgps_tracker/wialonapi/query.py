import json
from dataclasses import dataclass, field
from typing import Any

from wialon import flags as wialon_flag

from .session import WialonSession


@dataclass
class WialonQuery:
    items_type: str = "avl_unit"
    prop_name: str = "sys_name"
    sort_type: str = "sys_name"
    prop_type: str = "property"
    or_logic: int = 0
    _force: int = 0
    _flags: int = wialon_flag.ITEM_DATAFLAG_BASE
    _from: int = 0
    _to: int = 0
    _prop_value_mask: str = field(init=False, default="*")

    def __post_init__(self):
        if not hasattr(self, "prop_value_mask"):
            self.prop_value_mask = "*"
        else:
            self.prop_value_mask = self.prop_value_mask

    @property
    def prop_value_mask(self) -> str:
        return self._prop_value_mask

    @prop_value_mask.setter
    def prop_value_mask(self, value: str) -> None:
        self._prop_value_mask = f"*{value}*"

    def _gen_spec(self) -> dict[str, Any]:
        return {
            "itemsType": self.items_type,
            "propName": self.prop_name,
            "propValueMask": self.prop_value_mask,
            "sortType": self.sort_type,
            "propType": self.prop_type,
            "or_logic": self.or_logic,
        }

    def _gen_params(self) -> dict[str, Any]:
        return {
            "spec": self._gen_spec(),
            "force": self._force,
            "flags": self._flags,
            "from": self._from,
            "to": self._to,
        }

    def toggle_cache(self) -> None:
        self._force ^= 1

    def toggle_or_logic(self) -> None:
        self.or_logic ^= 1

    def set_flags(self, flags: list[int]) -> None:
        self._flags = sum(flags)

    def set_bounds(self, from_: int, to: int) -> None:
        self._from = from_
        self._to = to

    def execute(self, session: WialonSession) -> dict:
        params: dict = self._gen_params()
        return session.wialon_api.core_search_items(**params)
