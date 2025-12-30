from micropython import const
import time
import struct

# Register definitions
_COMMAND_BIT = const(0x80)
_REGISTER_ENABLE = const(0x00)
_REGISTER_ATIME = const(0x01)
_REGISTER_CONTROL = const(0x0F)
_REGISTER_SENSORID = const(0x12)
_REGISTER_STATUS = const(0x13)
_REGISTER_CDATA = const(0x14)

_ENABLE_AEN = const(0x02)
_ENABLE_PON = const(0x01)

_GAINS = (1, 4, 16, 60)
_ATIMES = [2.4, 24, 50, 100, 200, 400, 614.4]  # in ms


class TCS34725:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self._active = False
        self._integration_time = 2.4
        self._gain = 1

        # Check sensor ID
        sensor_id = self.sensor_id()
        if sensor_id not in (0x44, 0x4D, 0x10):
            raise RuntimeError("Wrong sensor id 0x{:x}".format(sensor_id))

        self.integration_time(self._integration_time)
        self.gain(self._gain)

    def _register8(self, reg, value=None):
        reg |= _COMMAND_BIT
        if value is None:
            return self.i2c.readfrom_mem(self.address, reg, 1)[0]
        self.i2c.writeto_mem(self.address, reg, struct.pack('<B', value))

    def _register16(self, reg, value=None):
        reg |= _COMMAND_BIT
        if value is None:
            data = self.i2c.readfrom_mem(self.address, reg, 2)
            return struct.unpack('<H', data)[0]
        self.i2c.writeto_mem(self.address, reg, struct.pack('<H', value))

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
            self._register8(_REGISTER_ENABLE, enable |
                            _ENABLE_PON | _ENABLE_AEN)
        else:
            self._register8(_REGISTER_ENABLE, enable & ~
                            (_ENABLE_PON | _ENABLE_AEN))

    def sensor_id(self):
        return self._register8(_REGISTER_SENSORID)

    def integration_time(self, ms=None):
        if ms is None:
            return self._integration_time
        ms = min(614.4, max(2.4, ms))
        self._integration_time = ms
        cycles = int(ms / 2.4)
        self._register8(_REGISTER_ATIME, 256 - cycles)
        return self._integration_time

    def gain(self, value=None):
        if value is None:
            return self._gain
        if value not in _GAINS:
            raise ValueError("Gain must be 1,4,16,60")
        self._gain = value
        self._register8(_REGISTER_CONTROL, _GAINS.index(value))
        return self._gain

    def _valid(self):
        return bool(self._register8(_REGISTER_STATUS) & 0x01)

    def read_raw(self):
        """Return raw R,G,B,C values"""
        was_active = self.active()
        if not was_active:
            self.active(True)
            time.sleep_ms(int(self._integration_time + 2))

        while not self._valid():
            time.sleep_ms(1)

        data = self.i2c.readfrom_mem(self.address, 0xA0 | _REGISTER_CDATA, 8)
        c, r, g, b = struct.unpack('<HHHH', data)

        if not was_active:
            self.active(False)
        return r, g, b, c

    def read(self, auto_adjust=True):
        """Return processed data: CCT and Lux if valid, else None, Lux"""
        r, g, b, c = self.read_raw()

        if auto_adjust:
            # Adjust gain/integration if saturated
            if c > 0.9 * 65535:
                if self._gain > 1:
                    self.gain(self._gain // 4)
                elif self._integration_time > 2.4:
                    self.integration_time(max(2.4, self._integration_time / 2))
            elif c < 1000:
                if self._gain < 60:
                    self.gain(min(60, self._gain * 4))
                elif self._integration_time < 614.4:
                    self.integration_time(
                        min(614.4, self._integration_time * 2))

        # CCT/Lux calculation only if valid (C not zero and not saturated)
        if c == 0 or c > 65535:
            return None, None
        # DN40 formula
        x = -0.14282*r + 1.54924*g + -0.95641*b
        y = -0.32466*r + 1.57837*g + -0.73191*b
        z = -0.68202*r + 0.77073*g + 0.56332*b
        d = x + y + z
        if d == 0:
            return None, y
        n = (x/d - 0.3320)/(0.1858 - y/d)
        cct = 449.0*n**3 + 3525.0*n**2 + 6823.3*n + 5520.33
        return cct, y


def html_rgb(data):
    r, g, b, c = data
    if c == 0:
        return 0, 0, 0
    red = int(pow((r/c), 2.5) * 255)
    green = int(pow((g/c), 2.5) * 255)
    blue = int(pow((b/c), 2.5) * 255)
    return red, green, blue


def html_hex(data):
    r, g, b = html_rgb(data)
    return "{:02x}{:02x}{:02x}".format(r, g, b)
