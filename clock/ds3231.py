"""This code controls a DS3231 breakout clock board.

Purchase: https://www.adafruit.com/product/3013
Datasheet: https://cdn-shop.adafruit.com/product-files/3013/DS3231.pdf
"""


class DS3231:
    """This class provides basic time controls."""

    def __init__(self, i2c, address=0x68):
        """Set up the board at default address 0x64."""
        self.i2c = i2c
        self.address = address

    @property
    def hour(self) -> int:
        """Get/store hour on the DS3231 board."""
        return _decodeByte(self.i2c.readfrom_mem(self.address, 0x02, 1))

    @hour.setter
    def hour(self, hour) -> None:
        if hour < 0 or hour > 23:
            raise ValueError("Hour must be between 0 and 23.")
        self._i2c.writeto_mem(self.address, 0x02, _encodeByte(hour))

    @property
    def minute(self) -> int:
        """Get/store minute on the DS3231 board."""
        return _decodeByte(self.i2c.readfrom_mem(self.address, 0x01, 1))

    @minute.setter
    def minute(self, minute) -> None:
        if minute < 0 or minute > 59:
            raise ValueError("Minute must be between 0 and 59.")
        self._i2c.writeto_mem(self.address, 0x01, _encodeByte(minute))

    @property
    def second(self) -> int:
        """Get second on the DS3231 board."""
        return _decodeByte(self.i2c.readfrom_mem(self.address, 0x00, 1))


def _decodeByte(byte) -> int:
    """Decode a byte value from the clock to decimal."""
    tens = (byte[0] >> 4) * 10
    ones = byte[0] & 0x0F
    return tens + ones


def _encodeByte(num) -> bytes:
    """Encode a decimal value for writing to the clock."""
    tens, ones = divmod(num, 10)
    return bytes([(tens << 4) + ones])
