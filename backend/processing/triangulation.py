"""
Real‑time TDOA triangulation + target tracking for WhisperNet
─────────────────────────────────────────────────────────────
Called by `classifier.py` AFTER a positive propeller detection.

Pipeline:
1. wake_peers()  → tells all other hydrophones to capture immediately
2. collect_arrival_times()  → waits until every hydrophone has a timestamp
3. locate()      → solves nonlinear hyperbolic least‑squares for (x, y)
4. track.update() → stores fix, computes speed v and heading θ
"""

from __future__ import annotations
import json
import math
import time
import numpy as np
from collections import deque
from pathlib import Path
from typing import Dict, Tuple, List
from scipy.optimize import least_squares

# 1. ––– CONFIG ––– pull hydrophone positions & constants
CFG = json.loads(Path("../config.json").read_text()) #changed this

C_SOUND = CFG.get("sound_speed", 1480.0)     # m s⁻¹ in seawater
HYDROS: Dict[str, Tuple[float, float]] = {h["id"]: (h["x"], h["y"])
                                          for h in CFG["hydrophones"]}
REF_ID = CFG["hydrophones"][0]["id"]         # first hydrophone is reference
WINDOW = CFG.get("velocity_window", 5)       # N fixes for speed/heading


# 2. ––– HYDROPHONE CONTROL (stub) –––
#     Replace with MQTT / WebSocket / RF wake‑up as needed.
def wake_peers(trigger_id: str) -> None:
    """Send a ‘wake & record now’ command to every hydrophone except trigger_id."""
    for hid in HYDROS:
        if hid != trigger_id:
            # PUT YOUR REAL COMMS HERE  (MQTT publish, socket.io emit, etc.)
            print(f"🔊  Waking hydrophone {hid}")



# 3. ––– TDOA 2‑D POSITION SOLVER  –––

def locate(arrival: Dict[str, float]) -> Tuple[float, float]:
    """
    arrival = {hydro_id: timestamp_seconds}
    Solves min_{x,y} Σ_k (‖(x,y)−(x_k,y_k)‖ − ‖(x,y)−(x_1,y_1)‖ − Δd_1k)²
    where Δd_1k = c·Δt_1k.
    """

    t_ref = arrival[REF_ID]

    # Build Δd vector (one per non‑ref hydrophone)
    deltas: List[Tuple[np.ndarray, float]] = []
    for hid, t in arrival.items():
        if hid == REF_ID:
            continue
        Δd = C_SOUND * (t - t_ref)                  # metres
        deltas.append((np.array(HYDROS[hid]), Δd))

    p1 = np.array(HYDROS[REF_ID])                   # reference coords (x₁,y₁)

    # Objective function for least_squares
    def residual(p: np.ndarray) -> np.ndarray:
        x, y = p
        r = []
        for pk, Δd in deltas:
            r.append(np.linalg.norm([x - pk[0], y - pk[1]])
                     - np.linalg.norm([x - p1[0], y - p1[1]])
                     - Δd)
        return np.array(r)

    # Initial guess → centroid of hydrophones
    init = np.mean(np.array(list(HYDROS.values())), axis=0)
    sol = least_squares(residual, init, method="lm")
    return sol.x[0], sol.x[1]



# 4. ––– VELOCITY / HEADING TRACKER –––

class Track:
    """Stores last N fixes and gives (speed m s⁻¹, heading rad)."""

    def __init__(self, window: int = WINDOW):
        self.buf: deque[Tuple[float, float, float]] = deque(maxlen=window)

    def update(self, x: float, y: float, t: float) -> Tuple[float | None, float | None]:
        self.buf.append((x, y, t))
        if len(self.buf) < 2:
            return None, None

        x_now, y_now, t_now = self.buf[-1]
        x_old, y_old, t_old = self.buf[0]
        dt = t_now - t_old
        v = math.hypot(x_now - x_old, y_now - y_old) / dt
        θ = math.atan2(y_now - y_old, x_now - x_old)
        return v, θ


track = Track()



# 5. ––– PUBLIC ENTRY POINT ––– called from classifier.py
def triangulate(trigger_id: str, trigger_time: float) -> None:
    """
    trigger_id   – hydrophone that first detected the propeller
    trigger_time – its detection timestamp in seconds (time.time())
    """

    # (1) Wake the sleeping units
    wake_peers(trigger_id)

    # (2) Gather arrival times.  In practice this would block until
    #     every hydrophone returns a timestamp for the same event ID.
    arrival = {trigger_id: trigger_time}
    arrival |= gather_other_arrivals(trigger_time)  # ← implement I/O yourself

    if len(arrival) < 3:
        print("⚠️  Need ≥3 hydrophones for TDOA; skipping triangulation")
        return

    # (3) Locate
    x, y = locate(arrival)
    v, θ = track.update(x, y, trigger_time)

    print(f"📍  Source at ({x:8.1f}, {y:8.1f}) m")
    if v is not None:
        print(f"🚢  v = {v:5.2f} m/s   θ = {math.degrees(θ):05.1f}°")

    #broadcast_detection({...})
    # TODO: push (x,y,v,θ) via WebSocket to the frontend_old



# 6. ––– SIMULATION HELPER (stub) –––
#     Replace with real inter‑device messaging.

def gather_other_arrivals(t0: float) -> Dict[str, float]:
    """
    BLOCKING placeholder that fabricates timestamps from the other
    hydrophones with random millisecond offsets.  Replace with real
    network I/O.
    """
    import random
    arrivals = {}
    for hid in HYDROS:
        if hid == REF_ID:
            continue
        # Simulate propagation delay up to ±0.020 s
        arrivals[hid] = t0 + random.uniform(-0.02, 0.02)
    return arrivals


# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick smoke test (simulated):
    triangulate(trigger_id=REF_ID, trigger_time=time.time())
