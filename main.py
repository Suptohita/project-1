from machine import I2C, Pin
from libs import tcs34725
from libs import rgb_led, button, pot_dimmer
from libs.tcs34725 import html_rgb
import time

def sleep(s):
    time.sleep(s)

# sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
Pin(19, Pin.OUT).value(0)
sensor = tcs34725.TCS34725(i2c)
# sensor.gain(5)

lock_btn = button.Button(23)

# rgb led
rgb = rgb_led.RGBLED(17, 5, 16)
sleep(0.001)
# target_color = rgb.generate_random_color(True)
rgb.set_color(255, 99, 0)
# print(f'Your Target Color is {target_color}')


dimmers = {}

dimmer_config = [
    {"name": "Green", "pot": 33, "led": 5},
    {"name": "Blue",  "pot": 35, "led": 16},
    {"name": "Red",   "pot": 32, "led": 17},
]

for item in dimmer_config:
    dimmer = pot_dimmer.PotDimmer(item["pot"], item["led"])
    dimmers[item["name"]] = dimmer


while True:
    status_msg = ""

    if lock_btn.was_pressed():
        pass

    for name, dimmer_obj in dimmers.items():
        val = dimmer_obj.update()
        status_msg += f"{name}:{val}  "

    print(status_msg, end='\r')
    time.sleep(0.05)