![alt text](image.png)
# Project L.U.M.E.N - Prism Cipher
## Introduction
Project L.U.M.E.N takes place in Sector 536 - A cosmic frontier within NYP , named after the classroom where it all began. This project is inspired by Singapore's growing investment in space research and technology. Sector 536 invites guests to explore a series of immersive space stationed at the edge of the unknown, these are the 4 exhibits :

Station 1 - Laser Defence Protocol
Station 2 - Kinetic Core Recharge
Station 3 - Chromatic Defence Simulator
Station 4 - Launch Core Override

  <h2 align = "center">
  Presented by:<br>
  <a href="https://github.com/syakiltrm"><img src="https://avatars.githubusercontent.com/u/208737626?v=4&size=64" title="tl0wh" width="40" height="40"></a>
  <a href="https://github.com/Kean-en"><img src="https://avatars.githubusercontent.com/u/109288203?v=4" title="AhSohs" width="40" height="40"></a>
  <a href="https://github.com/ArifYazid05"><img src="https://avatars.githubusercontent.com/u/208737017?v=4" title="srylqwerty" width="40" height="40"></a>
  <a href="https://github.com/Wayne-Teo"><img src="https://avatars.githubusercontent.com/u/208737553?v=4" title="dariensiew" width="40" height="40"></a>
</h2>



## Dependencies
### Hardware:
1. Raspberry Pi 4
2. Neopixel WS2812B
3. 5V DC Supply
4. Midi Controller
5. Push Button
6. GrandMA3
7. Yamaha QL1

### Software
1. RealVNC 
2. Visual Studio Code
3. Raspbian OS
4. Reaper
5. L-ISA
### Python Packages:
1. GPIO 
2. rpi_ws281x
3. mido
## System Diagram

mermaid
graph LR
A[Button]
B[Breadboard]
C[Raspberry PI]
D[Neopixel]
E[Midi Controller 1]
F[Midi Controller 2]

A --Ground--> B
A --One Wire--> C
B --Ground--> C
C --GPIO 18--> D
C --Ground--> D
C --USB--> E
C --USB--> F
Power --5V--> D

# MVP Code Logic

## run.py

```python
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


```
- Imports all necessary modules for GPIO, NeoPixel, OSC, and custom level scripts.
- Configures a NeoPixel LED strip with 120 LEDs connected to GPIO 18.
- Sets up GPIO 23 as the input pin for a physical button with a pull-up resistor.
- Establishes two OSC clients:
  - One for REAPER (audio cue controller).
  - One for GrandMA3 (lighting controller).

  ### `Button Hold` Function

```python
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
                  strip[i] = (255, 255, 255) if i < progress else(0, 0, 0)
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

```

- This function waits for the player to press and hold the physical button connected to GPIO 23.
- As the player holds the button, the NeoPixel strip progressively lights up white to show progress.
- If held for the defined `threshold` (default 2 seconds), it:
  - Sends marker `/marker/25` and `/action/1007` to REAPER via OSC to begin the game.
  - Turns off the LED strip and returns to continue execution.

### `main()` Function

```python
def main():
    try:
        wait_for_button_hold(threshold=2)
        level = Level_cycle.select_level()
        if level == 1:
            lvl_1.run_level_1(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 2:
            lvl_2.run_level_2(REAPER_CLIENT, LIGHT_CLIENT, strip)
        elif level == 3:
            lvl_3.run_level_3(REAPER_CLIENT, LIGHT_CLIENT, strip)
    except KeyboardInterrupt:
        print("[EXIT] Cleaning up GPIO")
        GPIO.cleanup()
```
- This is the main control function that coordinates the game setup and flow.
- It starts by calling `wait_for_button_hold()` to make sure the player wants to begin.
- Then it runs the level selection process using `Level_cycle.select_level()`.
- Based on the selected level, it calls the corresponding level function:
  - Level 1 → `run_level_1()`
  - Level 2 → `run_level_2()`
  - Level 3 → `run_level_3()`
- If the player presses Ctrl+C (keyboard interrupt), it cleans up the GPIO resources gracefully.


## Level_cycle.py

### `clear_board` Function
```python
def clear_board(outport):
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=0))
```
- Clears all pads on the Launchpad by sending a note_on message with velocity 0, turning off the lights

### `fill_board` Function
```python
def fill_board(outport, color):
    vel = COLOR_MAP[color]
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=vel))
```
- Fills the entire Launchpad grid with a specific color by translating the color into a MIDI velocity and sending it to every pad.

### `show_level` Function
```python
def show_level(outport, level):
    clear_board(outport)
    color = COLOR_MAP['green']
    for y in range(level):
        for x in range(8):
            outport.send(mido.Message('note_on', note=launchpad_grid[y][x], velocity=color))
```
- Visually shows the current level on the Launchpad by lighting up a number of rows in green equal to the level number.

### `fill_pixels` Function
```python
def fill_pixels(strip, color, ratio):
    count = int(ratio * strip.n)
    for i in range(strip.n):
        strip[i] = color if i < count else (0, 0, 0)
    strip.show()
```
- Used during button holding to progressively light up the NeoPixel strip based on how long the button is being held, giving visual feedback.

### `wait_for_start_button` Function
```python
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
```
- Waits for the player to press and hold the physical GPIO button. If the button is held for 2 seconds, it sends OSC messages to REAPER to trigger the game start. While holding, the NeoPixel strip progressively lights up in white as feedback.

### `select_level` Function
```python
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
```
- Handles the level selection process using the Launchpad:

- Top-left pad cycles through levels 1 to 3.

- Bottom-right pad confirms selection.

- Sends OSC messages /marker 26 and /marker 28 to REAPER when selection begins and is confirmed.

- Shows the current level visually by lighting rows on both Launchpads.










