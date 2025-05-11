import time
from backend.processing.classifier import classify_and_handle

# Path to test file
test_file = "../backend/processing/buffer/testAudio1.wav"

# Simulate a hydrophone ID and timestamp
hydrophone_id = "H1"
timestamp = time.time()

# Run the classification
classify_and_handle(test_file, hydrophone_id, timestamp)