from machine import Pin, PWM
import random

MAX_8BIT = 255
MAX_16BIT = 65_535
PWM_FREQ = 1_000


class RGBLED:
    """
    Control a single RGB LED using PWM.

    Attributes:
        pwm_r, pwm_g, pwm_b: PWM objects for red, green, blue pins
        invert: True for common-anode, False for common-cathode
    """

    def __init__(self, pin_r: int, pin_g: int, pin_b: int, invert: bool = True):
        """
        Initialize the RGB LED.

        Args:
            pin_r, pin_g, pin_b: GPIO pins connected to R, G, B
            invert: True if common-anode LED, False if common-cathode
        """
        self.invert = invert
        self.pwm_r = PWM(Pin(pin_r), freq=PWM_FREQ)
        self.pwm_g = PWM(Pin(pin_g), freq=PWM_FREQ)
        self.pwm_b = PWM(Pin(pin_b), freq=PWM_FREQ)

    def _clamp(self, value):
        return max(0, min(MAX_8BIT, value))

    def _to_u16(self, value_8bit):
        return value_8bit * 257

    def set_color(self, r, g, b):
        """Set the LED color."""
        r = self._clamp(r)
        g = self._clamp(g)
        b = self._clamp(b)

        dr = self._to_u16(r)
        dg = self._to_u16(g)
        db = self._to_u16(b)

        if self.invert:
            dr = MAX_16BIT - dr
            dg = MAX_16BIT - dg
            db = MAX_16BIT - db

        self.pwm_r.duty_u16(dr)
        self.pwm_g.duty_u16(dg)
        self.pwm_b.duty_u16(db)

    def generate_random_color(self, set_color=False):
        """Generate a random color and set it."""
        r = random.randint(0, MAX_8BIT)
        g = random.randint(0, MAX_8BIT)
        b = random.randint(0, MAX_8BIT)
        if set_color:
            self.set_color(r, g, b)
        print("Generated RGB:", r, g, b)
        return r, g, b
