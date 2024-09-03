import datetime
import logging
import pandas as pd
import requests

from pathlib import Path
from typing import Any

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.progress_bar import get_progress_bar

logging.basicConfig(level=logging.WARNING)


def get_url(host: str = "hst-api.wialon.com") -> str:
    return f"https://search-maps.wialon.com/{host}/gis_search?"

def get_data(street: str, sid: str) -> dict[str, str | int]:
    return {
        "street": street,
        "flags": sum([0x3, 0x100, 0x200, 0x400]),
        "count": 1,
        "indexFrom": 0,
        "uid": int("27881459"), # Terminus 1000's user id
        "sid": sid,
    }

def get_coords(street: str, sid: str) -> None | tuple[float, float]:
    url, data = get_url("hst-api.wialon.com"), get_data(street, sid)
    response = requests.post(url=url, data=data)
    if response.status_code == 200:
        item = response.json()[0].get("items")[0]
        return item.get("y"), item.get("x")
    return None


def extract_df(df: pd.DataFrame) -> list[dict[str, Any]]:
    extracted_data: list[dict[str, Any]] = []
    with WialonSession() as session:
        session_id: str = str(session.wialon_api.sid)
        print(f"Using Wialon session id: '{session_id}'...")
        for _, row in get_progress_bar(df, desc="Extracting coordinate pairs..."):
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

    return extracted_data

def save_output_df(data: list[dict[str, Any]]) -> Path:
    output_dir = Path("./output")
    if not output_dir.exists() or not output_dir.is_dir():
        output_dir.mkdir(exist_ok=True, parents=True)

    output_path: Path = output_dir / Path(f"geofences-{datetime.datetime.now():%Y-%m-%d-%M-%H-%S}.csv")
    df = pd.DataFrame(data)
    df.to_csv(output_path)

    return output_path
