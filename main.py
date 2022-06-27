"""Servo Clock.

Creates a 'digital' clock display using hobby servos,
two PCA9685 breakout boards, and a DS3231 precision
clock board.
"""
from machine import Pin, SoftI2C  # type: ignore
from clock import clock, ds3231, pca9685

if __name__ == "__main__":
    scl = Pin(22, pull=Pin.PULL_UP, mode=Pin.OPEN_DRAIN)
    sda = Pin(21, pull=Pin.PULL_UP, mode=Pin.OPEN_DRAIN)

    i2c = SoftI2C(scl, sda)

    minutes_duties = (
        (245, 450),
        (265, 470),
        (275, 460),
        (275, 491),
        (275, 491),
        (286, 491),
        (257, 491)
        # ToDo: Add more duties once servos are tested
    )

    hours_duties = (
        # ToDo: Add more duties once servos are tested
    )

    minutes = clock.Segment(pca9685.ServoController(i2c), minutes_duties)
    hours = clock.Segment(pca9685.ServoController(i2c, address=0x41),
                          hours_duties)
    clock_board = ds3231.DS3231(i2c)
    second = clock_board.second
    while True:
        if second != clock_board.second:
            second = clock_board.second
            print(f'{clock_board.hour:02}:{clock_board.minute:02}:\
                    {clock_board.second:02}')
            minutes.write(clock_board.minute)
            hours.write(clock_board.hour)
