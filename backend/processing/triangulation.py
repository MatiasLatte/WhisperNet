import numpy as np
import json
from pathlib import Path
from backend.processing.logger import read_timelog

# -------------------------------- Config --------------------------------
CONFIG_PATH = Path("../config.json")
TIMESTAMP_DIR = Path("timestamps")

with open(CONFIG_PATH) as f:
    config = json.load(f)

SPEED_OF_SOUND = config["sound_speed"]  # Make sure config uses this key

# -------------------------- TDOA Function --------------------------

def TDOA(TDOA_time_id_array:list) -> tuple:
    """
    Estimates 3D source location using Time Difference of Arrival (TDOA).
    Arguments:
        TDOA_time_id_array: List of [timestamp, {"x": .., "y": .., "z": ..}]
    Returns:
        Estimated (x, y, z) source location as a tuple
    """

    # ── backend/processing/triangulation.py ─────────────────────────────────────
    def TDOA(obs: list) -> tuple:
        """
        obs: list of [timestamp, {"x":..,"y":..,"z":..}]
        """
        if len(obs) < 4:
            print("⚠️ Need ≥4 hits for 3‑D solve")
            return (None,) * 3

        obs.sort(key=lambda t: t[0])
        t0, p0 = obs[0]
        x0, y0, z0 = p0["x"], p0["y"], p0["z"]

        A, b = [], []
        for ts, p in obs[1:]:
            dt = ts - t0
            xi, yi, zi = p["x"], p["y"], p["z"]
            A.append([xi - x0, yi - y0, zi - z0])

            rhs = 0.5 * (
                    SPEED_OF_SOUND ** 2 * dt ** 2
                    - (xi ** 2 + yi ** 2 + zi ** 2)
                    + (x0 ** 2 + y0 ** 2 + z0 ** 2)
            )
            b.append(rhs)

        A, b = np.asarray(A), np.asarray(b)
        try:
            sol, *_ = np.linalg.lstsq(A, b, rcond=None)
            return tuple(sol)
        except np.linalg.LinAlgError as err:
            print(f"⚠️ TDOA solve failed: {err}")
            return (None,) * 3


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

