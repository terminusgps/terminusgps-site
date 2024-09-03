import pandas as pd

from collections.abc import Collection
from tqdm import tqdm
from typing import Iterable


def get_progress_bar(collection: Collection, desc: str = "Iterating...") -> Iterable:
    match collection:
        case pd.DataFrame():
            iterator = collection.iterrows()
            colour = "#00ff00"
        case _:
            iterator = collection.__iter__()
            colour = "#ff0000"

    return tqdm(
        iterator,
        desc=desc,
        total=len(collection),
        ncols=75,
        ascii=False,
        colour=colour,
    )
