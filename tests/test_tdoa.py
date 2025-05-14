import numpy as np
from backend.processing.triangulation import TDOA, SPEED_OF_SOUND

def test_tdoa_central_point():
    # four hydrophones at unit cube corners
    hydros = [
        {"x":0,"y":0,"z":0},
        {"x":1,"y":0,"z":0},
        {"x":0,"y":1,"z":0},
        {"x":0,"y":0,"z":1},
    ]
    # put source dead‑centre (0.5,0.5,0.5)
    src = np.array([0.5,0.5,0.5])
    times = [np.linalg.norm(src - np.array([h["x"],h["y"],h["z"]]))/SPEED_OF_SOUND
             for h in hydros]

    obs = list(zip(times, hydros))
    est = np.array(TDOA(obs))
    assert np.allclose(est, src, atol=0.05)   # <5 cm error
