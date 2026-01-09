from machine import Pin
import time

class Button:
    def __init__(self, pin, pull=Pin.PULL_UP, debounce_ms=50):
        self.pin = Pin(pin, Pin.IN, pull)
        self.debounce_ms = debounce_ms
        self._last_state = self.pin.value()
        self._last_time = time.ticks_ms()

    def is_pressed(self):
        current = self.pin.value()
        now = time.ticks_ms()
        if current != self._last_state:
            self._last_time = now
            self._last_state = current
        if (time.ticks_diff(now, self._last_time) > self.debounce_ms) and (current == 0):
            return True
        return False
