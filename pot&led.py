
from machine import ADC, Pin, PWM
import time

# Potentiometer and LED pin mapping
CHANNELS = {
    "red":   {"pot": 26, "led": 17},
    "green": {"pot": 33, "led": 5},
    "blue":  {"pot": 35, "led": 16},
}

ADC_MAX = 4095
PWM_MAX = 1023
PWM_FREQ = 1000

pots = {}
leds = {}

# Setup ADCs and PWMs
for name, pins in CHANNELS.items():
    adc = ADC(Pin(pins["pot"]))
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)
    pots[name] = adc

    leds[name] = PWM(Pin(pins["led"]), freq=PWM_FREQ)

while True:
    values = {}

    for name, adc in pots.items():
        raw = adc.read()
        pwm = int(raw / ADC_MAX * PWM_MAX)
        leds[name].duty(pwm)
        values[name] = raw

    print(f"Red:{values['red']}, Green:{values['green']}, Blue:{values['blue']}", end='/r')
    time.sleep(0.05)


