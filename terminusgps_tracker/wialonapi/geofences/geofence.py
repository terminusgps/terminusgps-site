import pandas as pd

from dataclasses import dataclass
from wialon import WialonError

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.progress_bar import get_progress_bar

DEFAULT_OWNER_ID = int("27881459")
LINE = 1
POLYGON = 2
CIRCLE = 3
MAX_ZOOM = 19
MIN_ZOOM = 1

@dataclass
class GeofenceParams:
    perimeter: dict[str, float]
    owner_id: int = int(DEFAULT_OWNER_ID)
    geofence_id: int = 0
    call_mode: str = "create"
    name: str = ""
    description: str = ""
    geofence_type: int = CIRCLE
    flags: int = sum([0x10, 0x20, 0x40])
    color: int = int("80c800", 16)
    text_color: int = int("030303", 16)
    text_size: int = 12
    min_zoom: int = MIN_ZOOM
    max_zoom: int = MAX_ZOOM

    def to_dict(self) -> dict[str, str | int | dict[str, float]]:
        return {
            "itemId": self.owner_id,
            "id": self.geofence_id,
            "callMode": self.call_mode,
            "n": self.name,
            "d": self.description,
            "t": self.geofence_type,
            "f": self.flags,
            "c": self.color,
            "tc": self.text_color,
            "ts": self.text_size,
            "min": self.min_zoom,
            "max": self.max_zoom,
            "p": self.perimeter,
        }

def generate_params(row: pd.Series, owner_id: int = DEFAULT_OWNER_ID) -> GeofenceParams:
    return GeofenceParams(
        owner_id=owner_id,
        name=str(row["geofence_name"]),
        description=str(row["geofence_desc"]),
        perimeter={
            "x": float(row["geofence_lon"]),
            "y": float(row["geofence_lat"]),
            "r": int(row["geofence_r"]),
        }
    )

def create_geofence(row: pd.Series, *, owner_id: int = DEFAULT_OWNER_ID, session: WialonSession) -> str:
    """Creates a Wialon geofence based on a `pandas.Series` and returns its ID"""
    try:
        params_dict = generate_params(row, owner_id=owner_id).to_dict()
        response = session.wialon_api.resource_update_zone(**params_dict)
    except WialonError as e:
        raise e
    else:
        return str(response[0])

def create_geofences_from_df(df: pd.DataFrame, owner_id: int = DEFAULT_OWNER_ID) -> list[str]:
    """Creates Wialon geofences based on a `.csv` filepath, returns a list of their IDs"""
    try:
        with WialonSession() as session:
            geofence_ids = [
                create_geofence(row, owner_id=owner_id, session=session)
                for _, row
                in get_progress_bar(df, desc="Creating geofences...")
            ]
    except WialonError as e:
        raise e
    else:
        return geofence_ids

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
            print(f"Owner ID can only be 8 digits in length. '{cleaned_value}' has {len(cleaned_value)}.")
            return get_owner_id()
        elif not value:
            return DEFAULT_OWNER_ID
        else:
            return int(cleaned_value)

    user_input: str = str(input(f"Enter owner id for geofences [default: '{DEFAULT_OWNER_ID}']: "))
    return validate_owner_id(user_input)
