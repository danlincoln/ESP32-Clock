"""This code controls a PCA9685 PWM breakout board.

Purchase: https://www.amazon.com/dp/B07WS5XY63
Datasheet: https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
"""

import ustruct  # type: ignore
import machine  # type: ignore
from time import sleep_us


class PCA9685:
    """This class provides basic board memory controls."""

    def __init__(self, i2c: machine.SoftI2C,
                 address: int = 0x40) -> None:
        """Defaults board I2C address to 0x40 (see datasheet)."""
        self.i2c = i2c
        self.address = address
        self.pins = [PWMPin(self, i) for i in range(16)]
        self._reset()

    @property
    def frequency(self) -> int:
        """Get/Store the PWM frequency for the board.

        For more information on the prescaler formula used,
        see the PCA9685 datasheet §7.3.5, p.25.
        """
        scale = self.read_memory(0xFE)[0]
        return round(25_000_000 / (4096 * (scale + 1)))

    @frequency.setter
    def frequency(self, frequency: int) -> None:
        if not 24 <= frequency <= 1526:
            raise ValueError(f"Invalid PWM frequency ({frequency}Hz). \
                               Prescaler allows 24Hz - 1526Hz")
        scale = round(25_000_000 / (4096.0 * frequency))
        self.write_memory(0x00, [0x10])  # Clear Mode1 and set sleep bit.
        self.write_memory(0xFE, [scale])  # Write prescaler.
        self.write_memory(0x00, [0x00])  # Clear Mode1.
        sleep_us(500)
        self.write_memory(0x00, [0xA1])  # Set restart & auto-increment bits.

    def read_memory(self, memory_address: int,
                    length: int = 1, unpack: bool = True) -> tuple | bytes:
        """Read board memory.

        * address: Memory address to be read.
        * length: Number of bytes to read.
        * unpack: True (return unpacked tuple of bytes)/
        False (return raw bytes buffer).
        """
        if length == 1 or length % 2 == 0:
            data = self.i2c.readfrom_mem(self.address, memory_address, length)
            if unpack:
                return ustruct.unpack(f"<{length}B", data)
            else:
                return data
        else:
            raise ValueError(f"Invalid memory read length ({length}). \
                               Expects 1 (default) or a factor of 2.")

    def write_memory(self, memory_address: int,
                     values: bytes | tuple | list) -> None:
        """Write values to board memory.

        * address: Memory address to begin write.
        * values: Raw bytes to write or tuple/list of unpacked bytes to write.
        """
        if type(values) is bytes:
            data = values
        elif type(values) is tuple or type(values) is list:
            for value in values:
                if not 0 <= value <= 255:
                    raise ValueError(f"Byte value out of range ({value}). \
                                       Must be 0 <= value <= 255.")
            data = bytes(values)
        else:
            raise ValueError(f"Unexpected data type. Can write bytes, \
                               list, or tuple, not {type(values)}.")
        self.i2c.writeto_mem(self.address, memory_address, data)

    def _reset(self):
        # Clear Mode1 register.
        self.write_memory(0x00, [0x00])


class PWMPin:
    """This class provides basic duty/PWM operations for pins on the board."""

    def __init__(self, parent: PCA9685, index: int):
        """Set up PWM pin.

        * parent: PCA9685 object for memory operations.
        * index: Pin index 0-15.
        """
        self.index = index
        # Calculate first register address for this pin. Datasheet §7.3.3.
        self.address = 0x06 + (4 * self.index)
        self.parent = parent

    @property
    def pwm(self) -> tuple:
        """Get PWM on/off counts from memory."""
        pwm = self.parent.read_memory(self.address, 4, unpack=False)
        return ustruct.unpack("<2H", pwm)

    def set_pwm(self, on: int, off: int) -> None:
        """Set PWM on/off counts in memory."""
        if 0 <= on <= 4095 and 0 <= off <= 4096:
            data = ustruct.pack("<2H", on, off)
        else:
            raise ValueError(f"PCA9685 at {self.parent.address} attempted \
                               to set invalid PWM ({on}, {off}) on pin \
                               {self.index}.")
        self.parent.write_memory(self.address, data)

    @property
    def duty(self) -> int:
        """Get/Store PWM duty cycle."""
        on, off = self.pwm
        if on == 0 and off == 4096:
            value = 0
        elif on == 4096 and off == 0:
            value = 4095
        else:
            value = off
        return value

    @duty.setter
    def duty(self, value: int) -> None:
        try:
            value = self._duty_bound(value)
        except NotImplementedError:
            pass
        if value == 0:
            self.set_pwm(0, 4096)
        elif value == 4095:
            self.set_pwm(4096, 0)
        else:
            self.set_pwm(0, value)

    def _duty_bound(self, value: int) -> NotImplementedError:
        """Check that value is between set duty bounds.

        Implement checking in subclasses needing a bound range of min/max
        allowable duties.
        """
        raise NotImplementedError


class ServoController(PCA9685):
    """This class sets up a PCA9685 board for use as a servo controller."""

    def __init__(self, i2c: machine.SoftI2C, address: int = 0x40,
                 frequency: int = 50, min_duty: int = 180,
                 max_duty: int = 500) -> None:
        """Set up PCA9685 as a servo controller.

        * i2c: I2C object reference for memory operations.
        * address: The PCA9685's I2C address.
        * frequency: The board's PWM frequency.
        * min_duty: Board's servos' minimum allowable duty value.
        * max_duty: Board's servos' maximum allowable duty value.
        """
        self.i2c = i2c
        self.address = address
        # 4095 steps * pulse length us / (1,000,000 us i2c limit * frequency)
        self.min_duty, self.max_duty = min_duty, max_duty
        self.pins = [ServoPin(self, i) for i in range(16)]
        self._reset()
        self.frequency = frequency


class ServoPin(PWMPin):
    """This class sets up a PCA9685 PWM pin for use with a servo motor."""

    def __init__(self, parent: PCA9685, index: int) -> None:
        """Set up pin at index (0-15) on PCA9685 parent board."""
        super().__init__(parent, index)

    def _duty_bound(self, value: int) -> int:
        """Bind min/max allowable duties for value."""
        value = min(self.parent.max_duty, max(self.parent.min_duty, value))
        return value
