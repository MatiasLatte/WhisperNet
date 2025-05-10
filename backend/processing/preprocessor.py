import os
import librosa

# -------------------------------- Constants --------------------------------
SAMPLE_RATE = 22050           # Hz
DURATION = 2                  # seconds
N_MFCC = 13
N_FFT = 2048
HOP_LENGTH = 512
SAMPLES_PER_TRACK = SAMPLE_RATE * DURATION


def preprocess_audio(filepath: str) -> dict | None:
    """
    Preprocess a single .wav audio file and return its MFCC representation.

    Args:
        filepath (str): Path to the .wav file.

    Returns:
        dict: A JSON-like dictionary with keys:
              - "mfcc": 3D list [1, time, features]
              - "source_file": original filepath
        None: If file is invalid or too short.
    """

    if not os.path.isfile(filepath):
        return None

    try:
        signal, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)
    except Exception as e:
        return None

    if len(signal) < SAMPLES_PER_TRACK:
        return None

    signal = signal[:SAMPLES_PER_TRACK]

    mfcc = librosa.feature.mfcc(
        y=signal,
        sr=sr,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH
    ).T

    if mfcc.shape[0] == 0:
        return None

    return {
        "mfcc": [mfcc.tolist()],     # batched shape for model
        "source_file": filepath
    }
