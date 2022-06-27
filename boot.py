import network
import webrepl

with open('.password', 'r') as f:
    password = f.read()


webrepl.start()

ap = network.WLAN(network.AP_IF)
ap.config(essid="ESP32_CLOCK", password=password, authmode=3, hidden=1)
ap.active(True)
del(password)
