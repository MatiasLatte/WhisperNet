import numpy as np, builtins, types
from pathlib import Path
from backend.processing import classifier as mod

def test_classify_success(monkeypatch, sandbox):
    # ---- stub keras model (always “propeller”) ---------------------------
    class DummyModel:
        def predict(self, x): return np.array([[0.1, 0.9]])
    monkeypatch.setattr(mod.keras.models, "load_model",
                        lambda *_: DummyModel(), raising=False)

    # ---- stub preprocess_audio  (returns fake mfcc array) ---------------
    def fake_pre(path): return {"mfcc": np.zeros((1,130,13)).tolist()}
    monkeypatch.setattr(mod, "preprocess_audio", fake_pre)

    # ---- create a dummy wav in buffer/ ----------------------------------
    wav = Path("buffer/test.wav")
    wav.touch()

    ok = mod.classify_and_handle(str(wav), "H1", 123.0)
    assert ok is True                     # should flag propeller
    assert not wav.exists()               # file moved out of buffer

    dets = list(Path("detections").glob("*.json"))
    assert len(dets) == 1                 # detection metadata created
