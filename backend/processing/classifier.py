import shutil, os, json, numpy as np, time
from pathlib import Path
import keras #TODO: tensorflow.keras inaccessible python 3.12
from backend.processing.preprocessor import preprocess_audio
from backend.processing.triangulation import triangulate

MODEL_PATH = "WhisperNet_model.h5"

try:
    model = keras.models.load_model(MODEL_PATH)
except FileNotFoundError:
    print("⚠️  WARNING: Model file not found; classifier will always return ambient.")
    model = None  # stub
DETECT_DIR = Path("detections")
DETECT_DIR.mkdir(exist_ok=True, parents=True)




def classify_and_handle(filepath: str, hydro_id: str, timestamp: float) -> None:
    if model is None:
        print("No model -> treating as ambient noise")
        os.remove(filepath)
        return
    """Runs pre‑processing ➜ model ➜ handles results."""
    data = preprocess_audio(filepath)
    if data is None:
        print("Empty data")
        return

    x = np.array(data["mfcc"])[..., np.newaxis]  # shape: (1, 130, 13, 1)
    probs = model.predict(x)[0]
    cls   = int(np.argmax(probs))
    conf  = float(np.max(probs))


#triangulate(trigger_id=hydro_id, trigger_time=timestamp)
    if cls == 1:
        print(f"✅  Propeller — promoting to detections/")
        _store_detection(filepath, data, timestamp)
        #goes here
    else:
        print(f"🌊  Not a propeller — discarding")
        os.remove(filepath)             # clear the buffer slot


def _store_detection(src_wav: str, mfcc_data: dict, ts: float) -> None:
    """
    Copies the .wav from buffer/ into detections/ and drops a sibling JSON
    with MFCC + metadata.
    """
    stamp  = int(ts)
    base   = f"det_{stamp}"
    dst_wav = DETECT_DIR / f"{base}.wav"
    dst_json = DETECT_DIR / f"{base}.json"

    shutil.move(src_wav, dst_wav)            # move clip out of buffer
    mfcc_data["timestamp"] = ts
    with open(dst_json, "w") as fp:
        json.dump(mfcc_data, fp, indent=2)
