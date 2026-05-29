# Install once:
# sudo apt update
# sudo apt install -y python3-picamera2
#
# Optional camera check:
# rpicam-hello
#
# Run:
# python3 camera_full_test.py

from picamera2 import Picamera2
from time import sleep
from datetime import datetime

picam2 = Picamera2()

# Preview configuration
config = picam2.create_preview_configuration()
picam2.configure(config)

print("Starting camera...")
picam2.start()

# Allow autofocus/exposure to settle
sleep(3)

# Capture photo
filename = f"photo_{datetime.now():%Y%m%d_%H%M%S}.jpg"

print(f"Capturing {filename}")
picam2.capture_file(filename)

print("Photo saved!")

# Camera metadata
metadata = picam2.capture_metadata()

print("\nCamera Metadata")
print("-" * 30)

for key, value in metadata.items():
    print(f"{key}: {value}")

picam2.stop()

print("\nDone.")