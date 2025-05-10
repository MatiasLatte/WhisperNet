import time
from backend.processing.classifier import classify_and_handle

# Path to your test file
test_file = "buffer/22__19_07_13_adventure_maniobra copy.wav"

# Simulate a hydrophone ID and timestamp
hydrophone_id = "H1"
timestamp = time.time()

# Run the classification
classify_and_handle(test_file, hydrophone_id, timestamp)