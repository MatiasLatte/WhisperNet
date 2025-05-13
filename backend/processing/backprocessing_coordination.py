from backend.processing.hydro_capture import capture_and_log
from backend.processing.triangulation import TDOA
from time import time
import json
from pathlib import Path


CURRENT_TIME = 0
INITIAL_TIME = 0
CONFIG_PATH = Path("../config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

def passive_hearing() -> None:
    for hydro_id in config["hydrophones"]["id"]: #TODO: Check if this path through directories is accurate
        if CURRENT_TIME - INITIAL_TIME >= 10:
            detection_status = capture_and_log(hydro_id)
            if detection_status is True:
                #TODO: insert code to wake up all hydrophones
                active_hearing()
                break


def active_hearing() -> None:
    detection_status_array = []
    for hydro_id in config["hydrophones"]["id"]:
        detection_status_array.append(capture_and_log(hydro_id))
    total_count_of_positive_triggers = len([result for result in detection_status_array if result == True])
    TDOA_trigger_signal(total_count_of_positive_triggers)




def TDOA_trigger_signal(total_count_of_positive_triggers):
    if total_count_of_positive_triggers >= 4:
        TDOA()  # TODO: add as inputs to the function, pressure, temperature, and salinity
    elif total_count_of_positive_triggers >= 1:
        active_hearing()

def executing_hearing_program():
    while True:
        passive_hearing()