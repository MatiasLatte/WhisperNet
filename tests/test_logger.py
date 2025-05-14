from backend.processing.logger import log_capture, read_timelog
import time, json
from pathlib import Path

def test_log_and_read(sandbox):
    # act
    log_capture("H1", "dummy.wav")

    # assert file exists
    f = Path("timestamps/H1.json")
    assert f.exists()

    # assert reader returns a float close to now
    ts = read_timelog("H1")
    assert isinstance(ts, float)
    assert abs(ts - time.time()) < 1.0  # within 1 second