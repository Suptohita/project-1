from micropython import const
import time
import struct

# Register definitions
_COMMAND_BIT = const(0x80)
_REGISTER_ENABLE   = const(0x00)
_REGISTER_ATIME    = const(0x01)
_REGISTER_AILT     = const(0x04)
_REGISTER_AIHT     = const(0x06)
_REGISTER_APERS    = const(0x0C)
_REGISTER_CONTROL  = const(0x0F)
_REGISTER_SENSORID = const(0x12)
_REGISTER_STATUS   = const(0x13)
_REGISTER_CDATA    = const(0x14)
_REGISTER_RDATA    = const(0x16)
_REGISTER_GDATA    = const(0x18)
_REGISTER_BDATA    = const(0x1A)

_ENABLE_AIEN = const(0x10)
_ENABLE_AEN  = const(0x02)
_ENABLE_PON  = const(0x01)

_GAINS = (1, 4, 16, 60)
_CYCLES = (0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)

class TCS34725:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self._active = False
        self._integration_time = 0
        
        # Check sensor ID
        # 0x44 = TCS34725, 0x4D = TCS34727
        sensor_id = self.sensor_id()
        if sensor_id not in (0x44, 0x4D, 0x10):
            raise RuntimeError("Wrong sensor id 0x{:x}".format(sensor_id))
            
        self.integration_time(2.4)

    def _register8(self, register, value=None):
        register |= _COMMAND_BIT
        if value is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        self.i2c.writeto_mem(self.address, register, struct.pack('<B', value))

    def _register16(self, register, value=None):
        register |= _COMMAND_BIT
        if value is None:
            data = self.i2c.readfrom_mem(self.address, register, 2)
            return struct.unpack('<H', data)[0]
        self.i2c.writeto_mem(self.address, register, struct.pack('<H', value))

    def active(self, value=None):
        if value is None:
            return self._active
        value = bool(value)
        if self._active == value:
            return
        self._active = value
        enable = self._register8(_REGISTER_ENABLE)
        if value:
            self._register8(_REGISTER_ENABLE, enable | _ENABLE_PON)
            time.sleep_ms(3)
            self._register8(_REGISTER_ENABLE, enable | _ENABLE_PON | _ENABLE_AEN)
        else:
            self._register8(_REGISTER_ENABLE, enable & ~(_ENABLE_PON | _ENABLE_AEN))

    def sensor_id(self):
        return self._register8(_REGISTER_SENSORID)

    def integration_time(self, value=None):
        if value is None:
            return self._integration_time
        # Clamp value between 2.4 and 614.4
        value = min(614.4, max(2.4, value))
        cycles = int(value / 2.4)
        self._integration_time = cycles * 2.4
        # Write 2s complement of cycles
        return self._register8(_REGISTER_ATIME, 256 - cycles)

    def gain(self, value=None):
        if value is None:
            return _GAINS[self._register8(_REGISTER_CONTROL)]
        if value not in _GAINS:
            raise ValueError("Gain must be 1, 4, 16 or 60")
        return self._register8(_REGISTER_CONTROL, _GAINS.index(value))

    def _valid(self):
        return bool(self._register8(_REGISTER_STATUS) & 0x01)

    def read(self, raw=False):
        # Handle auto-activation
        was_active = self.active()
        if not was_active:
            self.active(True)
            # Wait for integration time to ensure valid data
            time.sleep_ms(int(self._integration_time + 2))
            
        # Wait for valid bit
        while not self._valid():
            time.sleep_ms(1)

        # OPTIMIZATION: Block read all 8 bytes (C, R, G, B) at once
        # Using 0xA0 ensures Auto-Increment Protocol is used
        # (Command bit 0x80 | Auto-Increment bit 0x20 | Address 0x14)
        data = self.i2c.readfrom_mem(self.address, 0xA0 | _REGISTER_CDATA, 8)
        
        # Unpack: Clear, Red, Green, Blue (Little Endian unsigned shorts)
        c, r, g, b = struct.unpack('<HHHH', data)

        if not was_active:
            self.active(False)

        if raw:
            return (r, g, b, c)
        return self._temperature_and_lux((r, g, b, c))

    def _temperature_and_lux(self, data):
        r, g, b, c = data
        if c == 0:
            return None, 0
        
        # DN40 calculations
        x = -0.14282 * r + 1.54924 * g + -0.95641 * b
        y = -0.32466 * r + 1.57837 * g + -0.73191 * b
        z = -0.68202 * r + 0.77073 * g +  0.56332 * b
        
        d = x + y + z
        if d == 0:
            return None, 0
            
        n = (x / d - 0.3320) / (0.1858 - y / d)
        
        # CCT Calculation
        cct = 449.0 * n**3 + 3525.0 * n**2 + 6823.3 * n + 5520.33
        
        return cct, y

def html_rgb(data):
    r, g, b, c = data
    if c == 0:
        return 0, 0, 0
    # Apply gamma correction (pow 2.5) and scaling
    red   = int(pow((int((r / c) * 256) / 255), 2.5) * 255)
    green = int(pow((int((g / c) * 256) / 255), 2.5) * 255)
    blue  = int(pow((int((b / c) * 256) / 255), 2.5) * 255)
    return red, green, blue

def html_hex(data):
    r, g, b = html_rgb(data)
    return "{:02x}{:02x}{:02x}".format(r, g, b)