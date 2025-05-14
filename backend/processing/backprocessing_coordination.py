from backend.processing.hydro_capture import capture_and_log
from backend.processing.triangulation import TDOA_preprocessor
from backend.processing.logger import read_timelog
from time import time
import json
from pathlib import Path


CONFIG_PATH = Path("../config.json")
TIMESTAMP_DIR = Path("timestamps")

with open(CONFIG_PATH) as f:
    config = json.load(f)

def passive_hearing() -> None:
    for h in config["hydrophones"]:
        hydro_id = h["id"] #TODO: Check if this path through directories is accurate
        last_logged_scan = read_timelog(hydro_id)
        if time() - last_logged_scan >= 10:
            detection_status = capture_and_log(hydro_id)
            if detection_status is True:
                #TODO: insert code to wake up all hydrophones
                active_hearing()


def active_hearing() -> None:
    detection_status_array = []
    for hydro_id in config["hydrophones"]["id"]:
        detection_status_array.append({"id":hydro_id, "status":capture_and_log(hydro_id)})
    total_count_of_positive_triggers = sum(1 for r in detection_status_array if r["status"])
    TDOA_trigger_signal(total_count_of_positive_triggers, detection_status_array)




def TDOA_trigger_signal(total_count_of_positive_triggers:int, detection_status_array:list) -> None:
    if total_count_of_positive_triggers >= 4:
        TDOA_preprocessor(detection_status_array)  # TODO: add as inputs to the function, pressure, temperature, and salinity
def run():
    while True:
        passive_hearing()