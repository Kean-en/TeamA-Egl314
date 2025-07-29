# Level_cycle.py

import mido
import time
import board
import neopixel
from rpi_ws281x import Color
import RPi.GPIO as GPIO

# NeoPixel setup
LED_COUNT = 120
strip = neopixel.NeoPixel(board.D18, LED_COUNT, brightness=0.5, auto_write=False)

# Button GPIO
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Launchpad ports
inport1 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
outport1 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
inport2 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0")
outport2 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0")

launchpad_grid = [[81 - 10 * r + c for c in range(8)] for r in range(8)]

COLOR_MAP = {
    'off': 0,
    'red': 5,
    'green': 21,
    'white': 122
}

def clear_board(outport):
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=0))

def fill_board(outport, color):
    vel = COLOR_MAP[color]
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=vel))

def show_level(outport, level):
    clear_board(outport)
    color = COLOR_MAP['green']
    for y in range(level):
        for x in range(8):
            outport.send(mido.Message('note_on', note=launchpad_grid[y][x], velocity=color))

def wait_for_start_button(reaper_client):
    print("[WAIT] Holding button for 2s to start...")
    hold_time = 2
    start_time = None
    filling = False

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            if start_time is None:
                start_time = time.time()
            held = time.time() - start_time

            # Fill visual
            if not filling:
                print("[FILL] Button held, filling NeoPixel white")
                filling = True

            fill_pixels(strip, (255, 255, 255), held / hold_time)
        else:
            if start_time:
                if time.time() - start_time >= hold_time:
                    print("[OSC] REAPER: /marker 25")
                    reaper_client.send_message("/marker", 25)
                    reaper_client.send_message("/action", 1007)
                    strip.fill((0, 0, 0))
                    strip.show()
                    return
            start_time = None
            filling = False
            strip.fill((0, 0, 0))
            strip.show()
        time.sleep(0.01)

def fill_pixels(strip, color, ratio):
    count = int(ratio * strip.n)
    for i in range(strip.n):
        strip[i] = color if i < count else (0, 0, 0)
    strip.show()

def select_level(reaper_client):
    level = 1
    print("[OSC] REAPER: /marker 26")
    reaper_client.send_message("/marker", 26)
    reaper_client.send_message("/action", 1007)

    show_level(outport1, level)
    show_level(outport2, level)

    while True:
        msg1 = inport1.receive(block=False)
        msg2 = inport2.receive(block=False)
        msg = msg1 or msg2
        if msg and msg.type == 'note_on' and msg.velocity > 0:
            note = msg.note

            if note == launchpad_grid[7][7]:  # bottom-right confirm
                print(f"[LEVEL] Confirmed Level {level} → /marker 28")
                reaper_client.send_message("/marker", 28)
                reaper_client.send_message("/action", 1007)
                clear_board(outport1)
                clear_board(outport2)
                return level

            if note == launchpad_grid[0][0]:  # top-left cycle
                level = (level % 3) + 1
                print(f"[LEVEL] Switched to Level {level}")
                show_level(outport1, level)
                show_level(outport2, level)
        time.sleep(0.01)
