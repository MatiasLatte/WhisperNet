"""
Shared fixtures + one‑time stubs for the whole suite.
"""

# --- make repo root importable ------------------------------------------------
import sys, types, json, pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# --- stub‑out keras before any test imports classifier -----------------------
dummy_keras        = types.ModuleType("keras")
dummy_keras.models = types.ModuleType("keras.models")

def _fake_load_model(*_args, **_kwargs):
    class DummyModel:
        def predict(self, x):
            import numpy as np
            return np.array([[0.1, 0.9]])   # always “propeller”
    return DummyModel()

dummy_keras.models.load_model = _fake_load_model
sys.modules["keras"] = dummy_keras    # ← makes `import keras` succeed everywhere

# --- sandbox fixture (unchanged) ---------------------------------------------
@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    for d in ("buffer", "detections", "timestamps"):
        (tmp_path / d).mkdir()
    monkeypatch.chdir(tmp_path)       # all relative paths now hit the sandbox
    yield tmp_path
