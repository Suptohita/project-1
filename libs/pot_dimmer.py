from machine import ADC, Pin, PWM


class PotDimmer:
    def __init__(self, pot_pin, led_pin, freq=1000):
        # 1. Setup Potentiometer (ADC)
        self.adc = ADC(Pin(pot_pin))
        self.adc.atten(ADC.ATTN_11DB)  # Full range: 3.3v
        self.adc.width(ADC.WIDTH_12BIT)  # Range 0-4095

        # 2. Setup LED (PWM)
        self.led = PWM(Pin(led_pin), freq=freq)
        self.led.duty(0)  # Start off

        self.ADC_MAX = 4095
        self.PWM_MAX = 255

    def update(self):
        """
        Reads the pot, updates the LED brightness, 
        and returns the current raw value.
        """
        raw_val = self.adc.read()

        # Map 0-4095 (ADC) to 0-255 (PWM)
        duty_cycle = (raw_val * self.PWM_MAX) // self.ADC_MAX

        self.led.duty(duty_cycle)
        return duty_cycle