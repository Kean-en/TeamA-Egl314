# run.py — Main entry point for memory game

import time
import mido
import RPi.GPIO as GPIO
from rpi_ws281x import Adafruit_NeoPixel, Color
from pythonosc.udp_client import SimpleUDPClient

import lvl_1
import lvl_2
import lvl_3
import Level_cycle

# === GPIO Button Setup ===
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# === OSC Clients ===
REAPER_CLIENT = SimpleUDPClient("192.168.254.12", 8000)
LIGHT_CLIENT = SimpleUDPClient("192.168.254.213", 2000)

# === NeoPixel Setup ===
LED_COUNT = 120
LED_PIN = 18
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN)
strip.begin()

# === MIDI Setup ===
inport1 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0")
outport1 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0")

inport2 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0")
outport2 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0")

# === Helpers ===
def send_marker(n: int):
    """Jump to REAPER marker n and auto-play."""
    REAPER_CLIENT.send_message("/marker", n)
    REAPER_CLIENT.send_message("/action", 1007)  # ▶ Play

def clear_launchpads():
    for note in range(128):
        outport1.send(mido.Message('note_off', note=note, velocity=0))
        outport2.send(mido.Message('note_off', note=note, velocity=0))

def strip_color_off():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def wait_for_2s_hold():
    print("Hold the button for 2 seconds to start the game...")
    hold_start = None
    progress_steps = LED_COUNT  # Each pixel = progress step

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            if hold_start is None:
                hold_start = time.time()

            held_time = time.time() - hold_start
            progress = min(int((held_time / 2.0) * progress_steps), LED_COUNT)

            # Fill NeoPixels based on hold time
            for i in range(LED_COUNT):
                if i < progress:
                    strip.setPixelColor(i, Color(0, 255, 0))  # Green fill
                else:
                    strip.setPixelColor(i, Color(0, 0, 0))    # Off
            strip.show()

            if held_time >= 2.0:
                print("[HOLD] 2-second hold detected. Game starting.")
                strip_color_off()
                return
        else:
            # Reset if released early
            hold_start = None
            strip_color_off()

        time.sleep(0.01)

# === Main ===
def main():
    wait_for_2s_hold()
    send_marker(25)  # 🎙️ Start dialog marker (with playback)

    while True:
        level = Level_cycle.select_level()  # sends marker 26 + 28 inside
        clear_launchpads()

        if level == 1:
            REAPER_CLIENT.send_message("/level_start", 1)
            lvl_1.run_level_1(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 2:
            REAPER_CLIENT.send_message("/level_start", 2)
            lvl_2.run_level_2(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 3:
            REAPER_CLIENT.send_message("/level_start", 3)
            lvl_3.run_level_3(REAPER_CLIENT, LIGHT_CLIENT, strip)

        clear_launchpads()
        strip_color_off()
        time.sleep(1)

# === Entry Point ===
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Game interrupted by user.")
        clear_launchpads()
        strip_color_off()
        GPIO.cleanup()
        exit(0)
