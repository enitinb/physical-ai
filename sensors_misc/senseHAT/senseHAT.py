# Install once:
# sudo apt update
# sudo apt install -y sense-hat
#
# Run:
# python3 sense_hat_full_test.py

from sense_hat import SenseHat
from time import sleep

sense = SenseHat()
sense.clear()

while True:
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()

    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    compass = sense.get_compass()

    print(f"Temp: {temp:.1f} °C")
    print(f"Humidity: {humidity:.1f} %")
    print(f"Pressure: {pressure:.1f} hPa")
    print(f"Accel: x={accel['x']:.2f}, y={accel['y']:.2f}, z={accel['z']:.2f}")
    print(f"Gyro:  x={gyro['x']:.2f}, y={gyro['y']:.2f}, z={gyro['z']:.2f}")
    print(f"Compass: {compass:.1f}°")
    print("-" * 40)

    sense.show_message(f"T {temp:.1f}C", scroll_speed=0.05)

    for event in sense.stick.get_events():
        print(f"Joystick: {event.direction} {event.action}")

        if event.direction == "middle" and event.action == "pressed":
            sense.clear()
            print("Stopped.")
            raise SystemExit


    sleep(3)
