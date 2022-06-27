# ESP32-Clock ⏰
This is a hobby project to build a 'digital' clock face using servos and a microcontroller. The servos will rotate a plastic plate to be face-on when a digit's segment is meant to appear on, and edge-on when it is meant to appear off.

## Materials
* [ESP32 Microcontroller](https://www.amazon.com/dp/B08246MCL5) (Bought a 3-pack—why not? They're cheap.)
* 2x [PCA9685 PWM Boards](https://www.amazon.com/dp/B07WS5XY63)
* [DS3231 Precision Clock Board](https://www.adafruit.com/product/3013)
* 28x [SG90 Hobby Servos](https://www.amazon.com/dp/B07L2SF3R4) (Like hotdogs and buns, there wasn't a good match for the number I needed.)

The ESP32 runs [Micropython](https://micropython.org/).

## Models
`./models/`
* `Servo Bracket.stl` This is the mounting bracket for the hobby servos. It holds the servo away from whatever surface so the face has space to rotate.
* `Digit Face.stl` This is the digit face. It's 200mm x 50mm, which will make this a big clock.

## Thanks
I wrote the board drivers in `./clock/` with the help of several older repos I found on GitHub. So, special thanks to the following contributors!

* https://github.com/notUnique/DS3231micro
* https://github.com/adafruit/micropython-adafruit-pca9685
