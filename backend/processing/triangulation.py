import numpy as np
import json
from pathlib import Path
from time import time

# -------------------------------- Config --------------------------------
CONFIG_PATH = Path("../config.json")
TIMESTAMP_DIR = Path("timestamps")

with open(CONFIG_PATH) as f:
    config = json.load(f)

SPEED_OF_SOUND = config["sound_speed"]  # Make sure your config uses this key

# -------------------------- TDOA Function --------------------------

def TDOA(trigger_id: str, trigger_time: float) -> tuple:
    """
    Estimates 3D source location using Time Difference of Arrival (TDOA).

    Returns:
        Tuple of (x, y, z) estimated position.
    """

    hydrophones = config["hydrophones"]
    timestamp_entries = get_recent_timestamps()

    # Build a dict for quick lookup
    timestamps = {entry["id"]: entry["timestamp"] for entry in timestamp_entries}

    hydro_data = []
    for h in hydrophones:
        h_id = h["id"]
        if h_id in timestamps:
            pos_dict = h["pos"]
            pos = [pos_dict["x"], pos_dict["y"], pos_dict["z"]]
            hydro_data.append({
                "id": h_id,
                "pos": pos,
                "timestamp": timestamps[h_id]
            })

    if len(hydro_data) < 4:
        print("⚠️ Not enough hydrophones with recent data.")
        return None

    # Reference: first hydrophone
    ref = hydro_data[0]
    ref_time = ref["timestamp"]
    ref_pos = np.array(ref["pos"])

    equations = []
    constants = []

    for h in hydro_data[1:]:
        delta_t = h["timestamp"] - ref_time
        d_diff = delta_t * SPEED_OF_SOUND
        pos = np.array(h["pos"])

        equations.append(2 * (pos - ref_pos))
        constants.append(
            np.sum(pos**2) - np.sum(ref_pos**2) - d_diff**2
        )

    A = np.vstack(equations)
    b = np.array(constants)

    est_pos, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return tuple(est_pos)

# ----------------------- Timestamp Reader ------------------------

def get_recent_timestamps(window=0.2):
    """
    Returns list of recent timestamp records from hydrophone JSON files.
    Only includes records updated within the last `window` seconds.
    """
    now = time()
    results = []

    for file in TIMESTAMP_DIR.glob("H*.json"):
        with open(file) as f:
            data = json.load(f)

        if abs(now - data["timestamp"]) <= window:
            hydro_id = file.stem
            results.append({
                "id": hydro_id,
                "timestamp": data["timestamp"],
                "filename": data.get("filename", None)
            })

    return results
