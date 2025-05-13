from backend.processing.hydro_capture import capture_and_log
from backend.processing.triangulation import TDOA
from time import time
import json
from pathlib import Path


CONFIG_PATH = Path("../config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

def compose_timelog_dictionary() -> None:
    last_logged_scan = {id:0 for id in config["hydrophones"]["id"]}
    global last_logged_scan

def passive_hearing() -> None:
    for hydro_id in config["hydrophones"]["id"]: #TODO: Check if this path through directories is accurate
        if time() - last_logged_scan[hydro_id] >= 10:
            detection_status = capture_and_log(hydro_id)
            if detection_status is True:
                #TODO: insert code to wake up all hydrophones
                active_hearing()
        last_logged_scan[hydro_id] = time()


def active_hearing() -> None:
    detection_status_array = []
    for hydro_id in config["hydrophones"]["id"]:
        detection_status_array.append(capture_and_log(hydro_id))
    total_count_of_positive_triggers = len([result for result in detection_status_array if result == True])
    TDOA_trigger_signal(total_count_of_positive_triggers)




def TDOA_trigger_signal(total_count_of_positive_triggers) -> None:
    if total_count_of_positive_triggers >= 4:
        TDOA()  # TODO: add as inputs to the function, pressure, temperature, and salinity
    elif total_count_of_positive_triggers >= 1:
        active_hearing()

def executing_hearing_program():
    compose_timelog_dictionary()
    while True:
        passive_hearing()