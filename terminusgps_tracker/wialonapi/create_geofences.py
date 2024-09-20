import pandas as pd

from time import perf_counter
from pprint import pprint

from terminusgps_tracker.wialonapi.geofences import (
    create_geofences_from_df,
    extract_df,
    get_owner_id,
    save_output_df,
)
from .session import WialonSession

def test() -> None:
    exec_start = perf_counter()
    test_data = pd.Series(
        data={
            "geofence_name": "Ambra Watkins",
            "geofence_desc": "12930 California Palm Ct",
            "geofence_group": "Clients",
            "geofence_lat": 35.1667785645,
            "geofence_lon": -117.808731079,
            "geofence_r": 100
        },
        index=None,
    )

    print(test_data)
    with WialonSession() as session:
        response = session.wialon_api.resource_get_zone_data(**{"itemId": get_owner_id()})
        print(response)
        pprint(response)

    print("Done!")
    exec_stop = perf_counter()
    print(f"Exec time: {exec_stop - exec_start:.2f}s")
    return None

def main() -> None:
    exec_start = perf_counter()
    input_df = pd.read_csv("/home/blake/input_data.csv")
    extracted_data = extract_df(input_df)
    print(f"Extracted {len(extracted_data)} coordinate pairs in total.")

    output_path = save_output_df(extracted_data)
    print(f"Saved results to '{output_path.absolute()}'")

    create_geofences = input("Create geofences with output data? [y/n]: ")
    if create_geofences != "y":
        pass
    else:
        owner_id = get_owner_id()
        df = pd.read_csv(output_path)
        ids = create_geofences_from_df(df, owner_id=owner_id)
        print(ids)

    print("Done!")
    exec_stop = perf_counter()
    print(f"Exec time: {exec_stop - exec_start:.2f}s")

    return None

if __name__ == "__main__":
    test()
