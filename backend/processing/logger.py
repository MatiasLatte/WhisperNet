import json
import time
from pathlib import Path

# -------------------------------- Constants --------------------------------
TIMESTAMP_DIR = Path("timestamps")
TIMESTAMP_DIR.mkdir(exist_ok=True)

def log_capture(hydro_id: str, filename: str):
    now = time.time()
    payload = {
        "timestamp": now,
        "filename": filename
    }
    path = TIMESTAMP_DIR / f"{hydro_id}.json"
    with open(path, "w") as f:
        json.dump(payload, f)

def read_timelog(hydro_id:str) -> float:
    with open(f"{TIMESTAMP_DIR}/{hydro_id}.json") as f:
        time_data = json.load(f)
        hydro_timestamp = time_data["timestamp"]
        return hydro_timestamp
