import pandas as pd

from typing import Any, Union

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.progress_bar import get_progress_bar

DEFAULT_OWNER_ID = int("27881459")

def generate_params(row: pd.Series, owner_id: int = DEFAULT_OWNER_ID) -> dict[str, Union[str, int, dict[str, Any]]]:
    return {
        "itemId": owner_id,
        "id": 0,
        "callMode": "create",
        "n": str(row["geofence_name"]),
        "d": str(row["geofence_desc"]),
        "t": 3,
        "f": sum([0x10, 0x20, 0x40]),
        "c": int("80c800", 16),
        "tc": int("030303", 16),
        "ts": 12,
        "min": 1,
        "max": 19,
        "p": {
            "x": float(row["geofence_lon"]),
            "y": float(row["geofence_lat"]),
            "r": int(row["geofence_r"]),
        }
    }

def create_geofence(row: pd.Series, owner_id: int = DEFAULT_OWNER_ID) -> None:
    """Creates a Wialon geofence based on a `pandas.Series` and returns its ID"""
    with WialonSession() as session:
        params = generate_params(row, owner_id=owner_id)
        session.wialon_api.resource_update_zone(**params)

def create_geofences_from_df(df: pd.DataFrame, owner_id: int = DEFAULT_OWNER_ID) -> list[None]:
    """Creates Wialon geofences based on a `.csv` filepath, returns a list of their IDs"""
    return [
        create_geofence(row, owner_id=owner_id)
        for _, row
        in get_progress_bar(df, desc="Creating geofences...")
    ]

def get_owner_id() -> int:
    """Validates and cleans user input for `owner_id` parameter"""
    def clean_owner_id(value: str) -> str:
        return value.strip()

    def validate_owner_id(value: str) -> int:
        cleaned_value = clean_owner_id(value)
        if not cleaned_value.isdigit():
            print(f"Owner ID can only contain digits. '{cleaned_value}' contains non-digits.")
            return get_owner_id()
        elif len(cleaned_value) != 8:
            print(f"Owner ID can only be 8 digits in length. '{cleaned_value}' is {len(cleaned_value)} digits in length.")
            return get_owner_id()
        elif not value:
            return DEFAULT_OWNER_ID
        else:
            return int(cleaned_value)

    user_input: str = str(input(f"Enter owner id for geofences [default: '{DEFAULT_OWNER_ID}']: "))
    return validate_owner_id(user_input)
