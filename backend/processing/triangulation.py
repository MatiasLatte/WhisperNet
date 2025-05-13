import numpy as np
import json
from pathlib import Path
from time import time

# -------------------------------- Config --------------------------------
CONFIG_PATH = Path("../config.json")
TIMESTAMP_DIR = Path("timestamps")

with open(CONFIG_PATH) as f:
    config = json.load(f)

SPEED_OF_SOUND = config["sound_speed"]  # Make sure config uses this key

# -------------------------- TDOA Function --------------------------

def TDOA() -> tuple:
    """
    Estimates 3D source location using Time Difference of Arrival (TDOA).

    Returns:
        Tuple of (x, y, z) estimated position.
    """


# ----------------------- Timestamp Reader ------------------------
