from machine import I2C, Pin, SPI
import machine
from libs import rgb_led, button, pot_dimmer, ili9341
from libs.tcs34725 import html_rgb
import time
from time import sleep_ms
from math import sin, pi


def sleep(s):
    time.sleep(s)


# colors
BLACK = ili9341.color565(0, 0, 0)
WHITE = ili9341.color565(255, 255, 255)
BLUE = ili9341.color565(0, 0, 255)
RED = ili9341.color565(255, 0, 0)
GREEN = ili9341.color565(0, 255, 0)

# screen config
SCREEN_W = 320
SCREEN_H = 240

# screen pins
TFT_CS = 5
TFT_DC = 21
TFT_RST = 22

# touch pins
YP = 27
XP = 25
YM = 26 
XM = 14

# screen setup
spi = SPI(2, baudrate=40000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
sleep(0.001)
display = ili9341.Display(spi, cs=Pin(TFT_CS), dc=Pin(
    TFT_DC), rst=Pin(TFT_RST), width=320, height=320, rotation=270)

display.draw_text8x8(80, 110, 'Game is starting...', BLUE)
sleep(0.3)

lock_btn = button.Button(4, debounce_ms=50)

# rgb led
rgb = rgb_led.RGBLED(15, 2, 17)
sleep(0.2)
target_color = rgb.generate_random_color(True)
display.clear(WHITE)
sleep(0.2)
display.draw_text8x8(10, 10, f'Your Target Color is...', RED)
display.draw_rectangle(10, 30, 300, 200, GREEN)
print(f'Your Target Color is {target_color}')

dimmers = {}

lock_btn = button.Button(4, debounce_ms=100)
continue_btn= button.Button(16, debounce_ms=100)
restart_btn = button.Button(12, debounce_ms=100)

dimmer_config = [
    {"name": "Green", "pot": 33, "led": 2 },
    {"name": "Blue",  "pot": 35, "led": 17},
    {"name": "Red",   "pot": 32, "led": 15},    
]

for item in dimmer_config:
    dimmer = pot_dimmer.PotDimmer(item["pot"], item["led"])
    dimmers[item["name"]] = dimmer


while True:
    status_msg = ""

    if lock_btn.was_pressed():
        print('Lock pressed...')
        pass
    if continue_btn.was_pressed():
        print('Continue pressed...')
        pass
    if restart_btn.was_pressed():
        machine.reset()
        print('Restart pressed.....')
        pass

    for name, dimmer_obj in dimmers.items():
        val = dimmer_obj.update()
        status_msg += f"{name}:{val}  "

    print(status_msg)
    time.sleep(0.05)
