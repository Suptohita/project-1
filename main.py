from machine import I2C, Pin
import time
from libs import tcs34725

# Initialize I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # change pins for your board

# Initialize sensor
sensor = tcs34725.TCS34725(i2c)

print("Sensor ID:", hex(sensor.sensor_id()))

while True:
    Pin(4, Pin.OUT).on()
    Pin(17, Pin.OUT).off()
    time.sleep(1)

    tcs34725.TCS34725.gain(16)
    print(tcs34725.TCS34725.sensor_id())
    
    # Raw RGBC values
    r, g, b, c = sensor.read(raw=True)
    print("Raw R,G,B,C:", r, g, b, c)

    # Color temperature & lux
    cct, lux = sensor.read()
    print("CCT:", cct, "Lux:", lux)

    # Optional: HTML-style color
    rgb = tcs34725.html_rgb((r, g, b, c))
    hex_color = tcs34725.html_hex((r, g, b, c))
    print("RGB:", rgb, "Hex:", hex_color)

    time.sleep(1)