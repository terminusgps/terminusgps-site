import terminusgps_tracker.wialonapi.flags as flag
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.constants import WIALON_ITEM_TYPES


def get_id_from_iccid(iccid: str, session: WialonSession) -> str | None:
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"={iccid}",
                "sortType": "sys_unique_id",
                "propType": "property",
                "or_logic": 0,
            },
            "force": 0,
            "flags": flag.DATAFLAG_UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if response.get("totalItemsCount", 0) != 1:
        return None
    return response["items"][0].get("id")


def get_coords_from_address(address: str) -> tuple[float, float] | tuple[None, None]:
    return None, None


def is_unique(value: str, session: WialonSession, items_type: str = "avl_unit") -> bool:
    if items_type not in WIALON_ITEM_TYPES:
        raise ValueError(f"'{items_type}' is an invalid Wialon item type.")
    result = session.wialon_api.core_check_unique(
        **{"type": items_type, "value": value.strip()}
    ).get("result")
    return not bool(result)
