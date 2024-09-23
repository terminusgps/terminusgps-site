import logging
import pandas as pd
import requests

from typing import Any

from terminusgps_tracker.wialonapi.session import WialonSession

logging.basicConfig(level=logging.WARNING)


def get_coords(street: str, sid: str) -> None | tuple[float, float]:
    def get_data(street: str, sid: str) -> dict[str, str | int]:
        return {
            "street": street,
            "flags": sum([0x3, 0x100, 0x200, 0x400]),
            "count": 1,
            "indexFrom": 0,
            "uid": int("27881459"), # Terminus 1000's user id
            "sid": sid,
        }

    url, data = "https://search-maps.wialon.com/hst-api.wialon.com/gis_search?", get_data(street, sid)
    response = requests.post(url=url, data=data)
    if response.status_code == 200:
        item = response.json()[0].get("items")[0]
        return item.get("y"), item.get("x")


def extract_df(df: pd.DataFrame) -> pd.DataFrame:
    extracted_data: list[dict[str, Any]] = []
    with WialonSession() as session:
        session_id = str(session.wialon_api.sid)
        print(f"Using Wialon session id: '{session_id}'...")
        for _, row in df:
            street: str = str(row["address_street"])
            coords = get_coords(street, session_id)
            if coords is None:
                raise ValueError(f"No coordinates found for '{street}'...")
            else:
                extracted_data.append({
                    "geofence_name": row["geofence_name"],
                    "geofence_desc": row["geofence_desc"] if not pd.isna(row["geofence_desc"]) else street,
                    "geofence_group": row["geofence_group"],
                    "geofence_lat": coords[0],
                    "geofence_lon": coords[1],
                    "geofence_r": 100,
                })

    return pd.DataFrame(extracted_data)
