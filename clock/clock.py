"""This code wraps a PCA9685 ServoController for use as a clock face."""
from clock import pca9685


class Segment:
    """This class controls a set of servos as a clock face.

    A Segment represents one PCA9685 board, so it controls
    up to 16 servos. One hour/minute segment needs 14 servos
    (7 per digit).
    """

    def __init__(self, board: pca9685.ServoController,
                 duties: list) -> None:
        """Set up the face segment.

        * board: The PCA9685 Servo Controller this class will control.
        * duties: List of (off, on) duty positions for each servo.
        """
        self.board = board
        self._duties = duties
        # Pins 0 - 6 are the 'ones' place.
        self.ones = [(index, pin) for index, pin in enumerate(range(7))]
        # Pins 7-13 are the 'tens' place.
        self.tens = [(index, pin) for index, pin in enumerate(range(7, 14))]

    def duties(self, pin: int) -> tuple:
        """Get off, on duties for the servo.

        If unspecified, supply the ServoController's min/max duties.
        """
        try:
            off, on = self._duties[pin]
        except IndexError:
            off, on = self.board.min_duty, self.board.max_duty
        return off, on

    def write(self, number: int) -> None:
        """Write a number to the clock face."""
        tens, ones = divmod(number, 10)
        for index, pin in self.ones:
            off, on = self.duties(pin)
            pin = self.board.pins[pin]
            if bits_representation[ones] & pow(2, index):
                pin.duty = on
            else:
                pin.duty = off
        for index, pin in self.tens:
            off, on = self.duties(pin)
            pin = self.board.pins[pin]
            if bits_representation[tens] & pow(2, index):
                pin.duty = on
            else:
                pin.duty = off


bits_representation = (
    # Bitwise representation for numeral at index.
    0x3F,  # 0 - on: segments 0, 1, 2, 3, 4, 5
    0x06,  # 1 - on: segments 1, 2
    0x5B,  # 2 - on: segments 0, 1, 3, 4, 6
    0x4F,  # 3 - on: segments 0, 1, 2, 3, 6
    0x66,  # 4 - on: segments 1, 2, 5, 6
    0x6D,  # 5 - on: segments 0, 2, 3, 5, 6
    0x7D,  # 6 - on: segments 0, 2, 3, 4, 5, 6
    0x07,  # 7 - on: segments 0, 1, 2
    0x7F,  # 8 - on: segments 0, 1, 2, 3, 4, 5, 6
    0x6F   # 9 - on: segments 0, 1, 2, 3, 5, 6
)
