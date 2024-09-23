import pandas as pd

from pathlib import Path
from typing import Union
from wialon.api import WialonError

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.geofences.progress_bar import get_progress_bar

DEFAULT_OWNER_ID = "27881459"

def get_params(zone_ids: list[str], group_name: str, owner_id: str) -> dict[str, Union[str, int, list]]:
    return {
        "itemId": str(owner_id),
        "id": 0,
        "callMode": "create",
        "n": group_name,
        "d": group_name.title() + " Description",
        "zns": zone_ids,
    }

def create_geofence_group(zone_ids: list[str], group_name: str, owner_id: str) -> None:
    try:
        with WialonSession() as session:
            params = get_params(zone_ids, group_name=group_name, owner_id=owner_id)
            session.wialon_api.resource_update_zones_group(**params)
    except WialonError as e:
        raise e

def create_geofence_groups(df: pd.DataFrame, owner_id: str = DEFAULT_OWNER_ID) -> None:
    try:
        for name in get_progress_bar(list(df["geofence_group"].unique()), desc="Creating groups..."):
            zone_ids: list[str] = [str(row["geofence_id"]) for _, row in df.iterrows() if row["geofence_group"] == name]
            create_geofence_group(zone_ids, group_name=name, owner_id=owner_id)
    except WialonError as e:
        raise e

def main() -> None:
    input_df = pd.read_csv(Path("/home/blake/Projects/terminusgps-site/output/geofences-2024-08-30-00-12-50.csv"))
    create_geofence_groups(input_df)

if __name__ == "__main__":
    main()
