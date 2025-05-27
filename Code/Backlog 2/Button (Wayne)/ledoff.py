from rpi_ws281x import *
import time
import signal
import sys
import random

# LED strip configuration:
LED_COUNT = 120
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 128
LED_INVERT = False

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 0))
strip.show()