# run.py

import RPi.GPIO as GPIO
import time
import board
import neopixel
from pythonosc.udp_client import SimpleUDPClient

import Level_cycle
import lvl_1
import lvl_2
import lvl_3

# --- NeoPixel Config ---
LED_COUNT = 120
LED_PIN = board.D18
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.5, auto_write=False)

# --- GPIO Setup ---
BUTTON_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- OSC Clients ---
REAPER_CLIENT = SimpleUDPClient("192.168.254.12", 8000)
LIGHT_CLIENT = SimpleUDPClient("192.168.254.213", 2000)


def wait_for_button_hold(threshold=2):
    print("[INFO] Waiting for button hold to start...")
    held_time = 0
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            start_time = time.time()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                held_time = time.time() - start_time
                progress = int((held_time / threshold) * LED_COUNT)
                for i in range(LED_COUNT):
                    strip[i] = (255, 255, 255) if i < progress else (0, 0, 0)
                strip.show()
                if held_time >= threshold:
                    print("[INFO] Button held long enough to start!")
                    REAPER_CLIENT.send_message("/marker/25", 1.0)
                    REAPER_CLIENT.send_message("/action", 1007)
                    strip.fill((0, 0, 0))
                    strip.show()
                    return
                time.sleep(0.01)
        time.sleep(0.01)


def main():
    try:
        wait_for_button_hold(threshold=2)
        level = Level_cycle.select_level()  # sends marker 26 and 28 inside

        if level == 1:
            lvl_1.run_level_1(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 2:
            lvl_2.run_level_2(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 3:
            lvl_3.run_level_3(REAPER_CLIENT, LIGHT_CLIENT, strip)

    except KeyboardInterrupt:
        print("[EXIT] Cleaning up GPIO")
        GPIO.cleanup()


if __name__ == "__main__":
    main()
