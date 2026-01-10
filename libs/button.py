from machine import Pin
import time

class Button:
    def __init__(self, pin_number, debounce_ms=200):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms
        self.last_press_time = 0
        self.last_state = 1 

    def was_pressed(self):
        """
        Checks if the button was just pressed.
        Returns True ONLY on the moment of the press (Falling Edge).
        """
        current_state = self.pin.value()
        is_pressed_now = False
        
        if current_state == 0 and self.last_state == 1:
            
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_press_time) > self.debounce_ms:
                self.last_press_time = current_time
                is_pressed_now = True
        
        self.last_state = current_state
        return is_pressed_now

    def is_held(self):
        """Returns True as long as the button is being held down."""
        return self.pin.value() == 0