from dataclasses import dataclass
from wialon import flags as wialon_flag
from enum import Enum
from typing import Any, TypeVar

E = TypeVar("E", bound="WialonProperty")


from terminusgps_tracker.wialonapi.session import WialonSession


class WialonItemsType(Enum):
    AVL_HW = "avl_hw"
    AVL_RESOURCE = "avl_resource"
    AVL_RETRANSLATOR = "avl_retranslator"
    AVL_ROUTE = "avl_route"
    AVL_UNIT = "avl_unit"
    AVL_UNIT_GROUP = "avl_unit_group"
    USER = "user"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<WialonItemsType: '{self.value}'>"


class WialonProperty(Enum):
    LOGIN_DATE = "login_date"
    PROFILEFIELD = "profilefield"
    REL_ACCOUNT_DISABLED_MOD_TIME = "rel_account_disabled_mod_time"
    REL_ACCOUNT_UNITS_USAGE = "rel_account_units_usage"
    REL_ADMINFIELD_NAME = "rel_adminfield_name"
    REL_ADMINFIELD_NAME_VALUE = "rel_adminfield_name_value"
    REL_ADMINFIELD_VALUE = "rel_adminfield_value"
    REL_BILLING_ACCOUNT_NAME = "sys_billing_account_name"
    REL_BILLING_PARENT_ACCOUNT_NAME = "sys_billing_parent_account_name"
    REL_BILLING_PLAN_NAME = "sys_billing_plan_name"
    REL_CREATION_TIME = "rel_creation_time"
    REL_CUSTOMFIELD_NAME = "rel_customfield_name"
    REL_CUSTOMFIELD_NAME_VALUE = "rel_customfield_name_value"
    REL_CUSTOMFIELD_VALUE = "rel_customfield_value"
    REL_GROUP_UNIT_COUNT = "rel_group_unit_count"
    REL_HW_TYPE_ID = "rel_hw_type_id"
    REL_HW_TYPE_NAME = "rel_hw_type_name"
    REL_IS_ACCOUNT = "rel_is_account"
    REL_LAST_MSG_DATE = "rel_last_msg_date"
    REL_PROFILEFIELD_NAME = "rel_profilefield_name"
    REL_PROFILEFIELD_NAME_VALUE = "rel_profilefield_name_value"
    REL_PROFILEFIELD_VALUE = "rel_profilefield_value"
    REL_USER_CREATOR_NAME = "rel_user_creator_name"
    RETRANSLATOR_ENABLED = "retranslator_enabled"
    SYS_ACCOUNT_BALANCE = "sys_account_balance"
    SYS_ACCOUNT_DAYS = "sys_account_days"
    SYS_ACCOUNT_DISABLED = "sys_account_disabled"
    SYS_ACCOUNT_ENABLE_PARENT = "sys_account_enable_parent"
    SYS_BILLING_ACCOUNT_GUID = "sys_billing_account_guid"
    SYS_COMM_STATE = "sys_comm_state"
    SYS_ID = "sys_id"
    SYS_NAME = "sys_name"
    SYS_PHONE_NUMBER = "sys_phone_number"
    SYS_PHONE_NUMBER2 = "sys_phone_number2"
    SYS_UNIQUE_ID = "sys_unique_id"
    SYS_USER_CREATOR = "sys_user_creator"

    def __add__(self: E, other: E) -> E:
        if not isinstance(other, WialonProperty):
            raise TypeError(
                f"Unsupported operand type(s) for +: 'WialonProperty' and '{type(other).__name__}'"
            )
        combined_value = f"{self.value},{other.value}"
        return self.__class__(combined_value)

    def __sub__(self: E, other: E) -> E:
        if not isinstance(other, WialonProperty):
            raise TypeError(
                f"Unsupported operand type(s) for -: 'WialonProperty' and '{type(other).__name__}'"
            )

        if "," not in self.value:
            new_value = "" if self.value == other.value else self.value
        else:
            values = self.value.split(",")
            try:
                values.remove(other.value)
            except ValueError:
                pass
            new_value = ",".join(values)

        return self.__class__(new_value) if new_value else self.__class__("")

    def __repr__(self) -> str:
        return f"<WialonProperty: '{self.value}'>"


@dataclass
class WialonQuery:
    items_type: WialonItemsType = WialonItemsType.AVL_UNIT
    prop_name: WialonProperty = WialonProperty.SYS_NAME
    sort_type: WialonProperty = WialonProperty.SYS_NAME
    prop_type: str = "property"
    prop_value_mask: str = "*"
    or_logic: int = 1
    _force: int = 0
    _flags: int = wialon_flag.ITEM_DATAFLAG_BASE
    _from: int = 0
    _to: int = 0

    def _gen_spec(self) -> dict[str, Any]:
        return {
            "itemsType": self.items_type.value,
            "propName": self.prop_name.value,
            "propValueMask": self.prop_value_mask,
            "sortType": self.sort_type.value,
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
        result = session.wialon_api.core_search_items(**params)
        return result


def imei_number_exists_in_wialon(imei_number: str, session: WialonSession) -> bool:
    query = WialonQuery()
    query.toggle_or_logic()
    query.prop_value_mask = f"*{imei_number}*"
    query.prop_name = WialonProperty.SYS_UNIQUE_ID
    query.sort_type = WialonProperty.SYS_UNIQUE_ID
    result = query.execute(session)

    total_items = int(result.get("totalItemsCount", 0))
    if total_items == 1:
        return True
    else:
        return False
