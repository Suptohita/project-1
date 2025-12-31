from machine import I2C, Pin
import time
from libs import tcs34725, rgb_led

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)
rgb = rgb_led.RGBLED(18, 4, 23, invert=True)

Pin(17, Pin.OUT).value(0)


def measure_color():
    sensor.active(True)
    time.sleep(1)

    total_r = 0
    total_g = 0
    total_b = 0
    total_lux = 0

    warmup_count = 5
    total_iterations = 50
    measured_count = 0

    for i in range(total_iterations):
        r, g, b, c = sensor.read_raw()
        html_r, html_g, html_b = tcs34725.html_rgb((r, g, b, c))

        # Clamp RGB to 0-255
        html_r = min(max(html_r, 0), 255)
        html_g = min(max(html_g, 0), 255)
        html_b = min(max(html_b, 0), 255)

        _, lux = sensor.read()

        print(f"Measured RGB: ({html_r}, {html_g}, {html_b}), Lux: {lux}")

        if i >= warmup_count:
            if i == warmup_count:
                print("Now Measuring")
            total_r += html_r
            total_g += html_g
            total_b += html_b
            if lux is not None and lux >= 0:
                total_lux += lux
            measured_count += 1

        time.sleep(0.2)

    sensor.active(False)

    avg_r = total_r // measured_count
    avg_g = total_g // measured_count
    avg_b = total_b // measured_count
    avg_lux = total_lux // measured_count if total_lux > 0 else 0

    return (avg_r, avg_g, avg_b), avg_lux


while True:
    user_input = input("Generate a random color: (y/n) ")

    if user_input.lower() == "y":
        random_color = rgb.set_random_color()
        time.sleep(1)

        measured_color, measured_lux = measure_color()
        print(
            f"Color of the LED is: {measured_color}, "
            f"Actual color is: {random_color}, "
            f"Lux: {measured_lux}"
        )

    elif user_input.lower() == "n":
        break

    else:
        print("Invalid input. Please enter 'y' or 'n'.")
