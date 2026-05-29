"""Sense HAT and Camera tools for the Raspberry Pi.

Simple tools over real hardware, used by pi_sensor_agent.py:
- read temperature and humidity (Sense HAT)
- read orientation (Sense HAT)
- capture a photo (Camera Module)
- show a message on the LED matrix (Sense HAT)

Needs: strands-agents, sense-hat, picamera2.
"""

from datetime import datetime
from time import sleep

from sense_hat import SenseHat
from picamera2 import Picamera2
from strands import tool

sense = SenseHat()


@tool
def read_environment() -> dict:
    """Read the temperature in Celsius and humidity in percent."""
    return {
        "temperature_c": round(sense.get_temperature(), 1),
        "humidity_percent": round(sense.get_humidity(), 1),
    }


@tool
def read_orientation() -> dict:
    """Read the orientation as pitch, roll, and yaw in degrees."""
    o = sense.get_orientation_degrees()
    return {
        "pitch": round(o["pitch"], 1),
        "roll": round(o["roll"], 1),
        "yaw": round(o["yaw"], 1),
    }


@tool
def capture_image() -> dict:
    """Take a photo with the camera and save it to a timestamped file."""
    filename = f"photo_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    cam = Picamera2()
    cam.start()
    sleep(2)
    cam.capture_file(filename)
    cam.close()
    return {"saved": filename}


@tool
def show_message(text: str) -> dict:
    """Scroll a short message across the LED matrix.

    Args:
        text: Message to display.
    """
    sense.show_message(text)
    sense.clear()
    return {"displayed": text}
