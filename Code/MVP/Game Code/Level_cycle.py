# Level_cycle.py

import RPi.GPIO as GPIO
import time
import threading
import mido
import random
from rpi_ws281x import Color, Adafruit_NeoPixel
from pythonosc import udp_client

BUTTON_PIN = 17

# === OSC CLIENT SETUP ===
REAPER_CLIENT = udp_client.SimpleUDPClient("192.168.254.12", 8000)
LIGHT_CLIENT = udp_client.SimpleUDPClient("192.168.254.213", 2000)

# === MIDI Setup ===
MIDI_PORT = "Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0"
inport = mido.open_input(MIDI_PORT)
outport = mido.open_output(MIDI_PORT)

# === NeoPixel Setup ===
LED_COUNT = 120
LED_PIN = 18
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN)
strip.begin()

# === Launchpad Grid ===
launchpad_grid = [[(r + 1) * 10 + (c + 1) for c in range(8)] for r in range(8)]

LEVEL_SHAPES = {
    0: [launchpad_grid[0][4], launchpad_grid[1][4], launchpad_grid[2][4], launchpad_grid[3][4], launchpad_grid[4][4]],
    1: [launchpad_grid[0][3], launchpad_grid[0][4], launchpad_grid[0][5],
        launchpad_grid[1][3],
        launchpad_grid[2][3], launchpad_grid[2][4], launchpad_grid[2][5],
        launchpad_grid[3][5],
        launchpad_grid[4][3], launchpad_grid[4][4], launchpad_grid[4][5]],
    2: [launchpad_grid[0][3], launchpad_grid[0][4], launchpad_grid[0][5],
        launchpad_grid[1][5],
        launchpad_grid[2][3], launchpad_grid[2][4], launchpad_grid[2][5],
        launchpad_grid[3][5],
        launchpad_grid[4][3], launchpad_grid[4][4], launchpad_grid[4][5]]
}

# Confirm block: bottom right 2x2
CONFIRM_BLOCK = [launchpad_grid[y][x] for y in range(6, 8) for x in range(6, 8)]

COLOR_OFF = 0
COLOR_GREEN = 21
COLOR_BLUE = 73

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button_event = threading.Event()
level_index = 0

def show_solid_color(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def get_random_color():
    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255),
              Color(255, 255, 0), Color(255, 0, 255), Color(0, 255, 255)]
    return random.choice(colors)

def button_callback(channel):
    button_event.set()

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

def clear_launchpad():
    for note in range(0, 128):
        outport.send(mido.Message('note_on', note=note, velocity=COLOR_OFF))

def draw_level_selection(index):
    clear_launchpad()
    for note in LEVEL_SHAPES[index]:
        outport.send(mido.Message('note_on', note=note, velocity=COLOR_BLUE))
    for note in CONFIRM_BLOCK:
        outport.send(mido.Message('note_on', note=note, velocity=COLOR_GREEN))

def select_level():
    global level_index
    cooldown_until = time.time() + 3  # prevent button triggers for 3s

    # === Lighting startup ===
    print("[OSC] LIGHT: Off thru Sequence")
    LIGHT_CLIENT.send_message("/gma3/cmd", "Off thru Sequence")

    print("[OSC] LIGHT: Go+ Sequence 52")
    LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 52")

    # Clear MIDI buffer
    try:
        while True:
            msg = inport.receive(block=False)
            if msg is None:
                break
    except:
        pass

    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)
    time.sleep(0.1)

    print("Press button to cycle levels. Press 2x2 green block to confirm.")
    draw_level_selection(level_index)
    show_solid_color(get_random_color())

    while True:
        if button_event.is_set():
            # Debounce window active: ignore early button press
            if time.time() < cooldown_until:
                print("[DEBOUNCE] Skipping early button press to protect /marker/25")
                button_event.clear()
                continue

            # Handle level cycling
            button_event.clear()
            level_index = (level_index + 1) % 3
            draw_level_selection(level_index)
            show_solid_color(get_random_color())

         

            print("[OSC] REAPER: /marker/26")
            REAPER_CLIENT.send_message("/marker/26", 1.0)

            time.sleep(0.3)

        msg = inport.receive(block=False)
        if msg and msg.type == 'note_on' and msg.velocity > 0:
            if msg.note in CONFIRM_BLOCK:
                clear_launchpad()
                print("Level confirmed. Waiting for new selection...")

                while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    time.sleep(0.01)
                time.sleep(0.5)

                return level_index + 1

        time.sleep(0.01)
