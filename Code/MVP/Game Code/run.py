# run.py — Entry point for the full game

from Level_cycle import select_level
import lvl_1
import lvl_2
import lvl_3
import RPi.GPIO as GPIO
from rpi_ws281x import Color, Adafruit_NeoPixel
import mido
import sys
import time
import threading
from pythonosc import udp_client

# === OSC CLIENT SETUP ===
REAPER_CLIENT = udp_client.SimpleUDPClient("192.168.254.12", 8000)
LIGHT_CLIENT = udp_client.SimpleUDPClient("192.168.254.213", 2000)

# === NeoPixel Setup ===
LED_COUNT = 120
LED_PIN = 18
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN)

# === MIDI Setup === (for both Launchpads)
MIDI_PORTS = [
    "Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0",
    "Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0"
]
outports = [mido.open_output(p) for p in MIDI_PORTS]

# === GPIO Setup for Button Hold Start and Stop ===
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# === Helper for NeoPixel color ===
def show_color(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def clear_pixels():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def clear_launchpad():
    for outport in outports:
        for note in range(0, 128):
            outport.send(mido.Message('note_on', note=note, velocity=0))

def stop_game():
    print("[Game Paused] Game is now stopped.")
    show_color(Color(255, 0, 0))  # Red indicator
    clear_launchpad()
    clear_pixels()
    wait_for_button_hold()

# === Global Stop Watcher Thread ===
def monitor_stop():
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            start_time = time.time()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                if time.time() - start_time >= 4:
                    stop_game()
                time.sleep(0.1)
        time.sleep(0.1)

def wait_for_button_hold():
    print("Hold the button to start the game (2s)...")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            start_time = time.time()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                held_duration = time.time() - start_time
                if held_duration >= 2.0:
                    show_color(Color(0, 255, 0))  # Green for start
                else:
                    show_color(Color(0, 0, 255))  # Blue for just holding
                time.sleep(0.05)
            held_time = time.time() - start_time
            clear_pixels()
            if held_time >= 2.0:
                print("Game resuming...")

                # === Send OSC commands ===
                print("[OSC] REAPER: /marker/25")
                REAPER_CLIENT.send_message("/play", 1.0)
                REAPER_CLIENT.send_message("/marker/25", 1.0)

                print("[OSC] LIGHT: Off thru Sequence")
                LIGHT_CLIENT.send_message("/gma3/cmd", "Off thru Sequence")

                print("[OSC] LIGHT: Go+ Sequence 53")
                LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 53")

                return
            else:
                print("Hold longer to start.")

def main():
    try:
        strip.begin()

        # Start stop monitor thread
        stop_thread = threading.Thread(target=monitor_stop, daemon=True)
        stop_thread.start()

        wait_for_button_hold()

        while True:
            level = select_level()

            if level == 1:
                lvl_1.run_level_1(REAPER_CLIENT, LIGHT_CLIENT, strip)
            elif level == 2:
                lvl_2.run_level_2(REAPER_CLIENT, LIGHT_CLIENT, strip)
            elif level == 3:
                lvl_3.run_level_3(REAPER_CLIENT, LIGHT_CLIENT, strip)
            else:
                print("Invalid level selected.")

            clear_pixels()
            clear_launchpad()

    except KeyboardInterrupt:
        print("Game interrupted.")
        clear_pixels()
        clear_launchpad()
        GPIO.cleanup()
        sys.exit(0)

if __name__ == '__main__':
    main()

