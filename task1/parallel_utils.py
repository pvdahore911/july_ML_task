"""
Helper module for Task 1 - Level 3 (parallelization).
Kept in a separate .py file (not inline in the notebook) because
ProcessPoolExecutor needs to pickle the worker function, which is
unreliable when the function is defined directly inside a Jupyter
notebook cell. Importing it from a real module avoids that problem
entirely.
"""
import pandas as pd
import numpy as np


def parse_and_clean_year_range(args):
    """
    Worker function: parses ONLY the soundings whose YEAR falls inside
    [year_start, year_end] from the raw IGRA file, cleans them, and
    returns a single tidy DataFrame for that chunk.
    """
    filepath, year_start, year_end = args
    headers, records = [], []
    current_id = -1
    keep = False

    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("#"):
                current_id += 1
                year = int(line[13:17])
                keep = year_start <= year <= year_end
                if keep:
                    headers.append(dict(
                        sounding_id=current_id,
                        year=year,
                        month=int(line[18:20]),
                        day=int(line[21:23]),
                        hour=int(line[24:26]),
                    ))
            elif keep:
                records.append(dict(
                    sounding_id=current_id,
                    press=int(line[9:15]),
                    gph=int(line[16:21]),
                    temp=int(line[22:27]),
                    rh=int(line[28:33]),
                ))

    if not records:
        return pd.DataFrame()

    dfh = pd.DataFrame(headers)
    dfl = pd.DataFrame(records)
    dfl[["press", "gph", "temp", "rh"]] = dfl[[
        "press", "gph", "temp", "rh"]].replace([-9999, -8888], np.nan)
    dfl["press_hpa"] = dfl["press"] / 100
    dfl["temp_c"] = dfl["temp"] / 10
    dfl["rh_pct"] = dfl["rh"] / 10

    return dfl.merge(dfh, on="sounding_id")
