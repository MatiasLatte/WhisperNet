import numpy as np
import json
from pathlib import Path
from backend.processing.logger import read_timelog

# -------------------------------- Config --------------------------------
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"
TIMESTAMP_DIR = Path("timestamps")

with open(CONFIG_PATH) as f:
    config = json.load(f)

SPEED_OF_SOUND = config["sound_speed"]  # Make sure config uses this key

# -------------------------- TDOA Function --------------------------


def TDOA(obs: list) -> tuple:
    """
    obs : list of [timestamp, {"x":..,"y":..,"z":..}]
    Returns estimated (x,y,z) or (None,None,None) on failure
    """
    if len(obs) < 4:
        print("⚠️ Need ≥4 detections for 3‑D solve")
        return (None,)*3

    # Choose the earliest arrival as reference
    obs.sort(key=lambda t: t[0])
    t0, p0 = obs[0]
    x0, y0, z0 = p0["x"], p0["y"], p0["z"]

    A, b = [], []
    for ti, pi in obs[1:]:
        xi, yi, zi = pi["x"], pi["y"], pi["z"]
        A.append([xi - x0, yi - y0, zi - z0])

        ri2 = xi**2 + yi**2 + zi**2
        r02 = x0**2 + y0**2 + z0**2
        b.append(0.5 * (ri2 - r02 - SPEED_OF_SOUND**2 * (ti**2 - t0**2)))

    import numpy as np
    try:
        sol, *_ = np.linalg.lstsq(np.asarray(A), np.asarray(b), rcond=None)
        return tuple(sol)
    except np.linalg.LinAlgError as err:
        print(f"⚠️ TDOA solve failed: {err}")
        return (None,)*3


# ----------------------- Timestamp Reader ------------------------
def TDOA_preprocessor(detection_status_array:list)->None:
    TDOA_time_id_array = []
    for hydro_dict in detection_status_array:
        if hydro_dict["status"] == True:
            hydro_id = hydro_dict["id"]

            matching_hydro = next(
                (h for h in config["hydrophones"] if h["id"] == hydro_id), None
            )
            if matching_hydro:
                timestamp = read_timelog(hydro_id)
                if timestamp is None:
                    continue
                if "pos" in matching_hydro:
                    position = matching_hydro["pos"]

                else:
                    position = {k: matching_hydro[k] for k in ("x", "y", "z")}

                TDOA_time_id_array.append([timestamp, position])
    TDOA(TDOA_time_id_array)

