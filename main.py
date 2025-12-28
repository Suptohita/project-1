# main.py
from machine import Pin
from time import sleep

led = Pin(4, Pin.OUT)  # LED connected to GPIO 4

while True:
    led.value(1)  # Turn LED on
    print("LED is ON")
    sleep(0.3)    # Wait 0.5 seconds
    led.value(0)  # Turn LED off
    print("LED is OFF")
    sleep(0.3)    # Wait 0.5 seconds

