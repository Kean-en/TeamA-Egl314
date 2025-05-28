![alt text](image.png)
# Project L.U.M.E.N - Prism Cipher
## Introduction
Colours will be randomised and flashed on the colour wheel (neopixel) to win, 2 players must tap the midi pad in the correct sequence shown by the colour wheel within a time limit

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

### Software
1. RealVNC 
2. Visual Studio Code
3. Raspbian OS
### Python Packages:
1. GPIO 
2. rpi_ws281x
3. mido
## System Diagram

```mermaid
graph LR
A[Button]
B[Breadboard]
C[Raspberry PI]
D[Neopixel]
E[Midi Controller]

A --Ground--> B
A --One Wire--> C
B --Ground--> C
C --GPIO 18--> D
C --Ground--> D
C --USB--> E
Power --5V--> D
```

## Code Logic
<h3> Neopixel: </h3>
<h4> 1. Configuration </h4>

Sets up the LED strip:

```python
LED_COUNT = 120         # Total number of LEDs in the strip
LED_PIN = 18            # GPIO pin (must support PWM)
LED_FREQ_HZ = 800000    # LED signal frequency in hertz
LED_DMA = 10            # DMA channel for generating signal
LED_BRIGHTNESS = 128    # Brightness (0–255)
LED_INVERT = False      # True if using an inverting level shifter
```

<h4> 2. Color Definitions </h4>
 Colour names to RGB values using the Color(r,g,b) function:

```python
COLORS = {
    'red': Color(255, 0, 0),
    'green': Color(0, 255, 0),
    'yellow': Color(128, 51, 0),
    'brown': Color(40, 10, 0)
}
```
<h4> 3. Helper functions </h4>

### `clear_pixels()`
Turns off all LEDs by setting them to `(0, 0, 0)` and calling `.show()`.
### `signal_handler(sig, frame)`
Handles Ctrl+C (SIGINT) by turning off LEDs and exiting the program gracefully.
### `display_sequence(color_sequence)`
Displays a sequence of colors across the LED strip:
- Divides LEDs evenly among the colors.
- Lights up each segment with the corresponding color.
### `get_color_value(prompt)`
Prompts the user to input RGB values (0–255) for testing custom colors.


<h4> 4. Main Menu </h4>
Inside the `main()` loop, the user is presented with the following options:

1. **Custom Color Sequence**:  
   - Input comma-separated colors (e.g. `red,green`).
   - The LED strip is divided evenly and filled with these colors.

2. **Turn Off and Exit**:  
   - Clears the strip and exits the program.

3. **Flashbang**:  
   - Sets all LEDs to a bright warm white color (255, 240, 200).

4. **RGB Test**:  
   - Asks the user for red, green, and blue values.
   - Lights the strip with the specified color.

5. **Randomiser**:  
   - Randomly shuffles the 4 preset colors.
   - Displays them as a color sequence with no repetition.

<h4> 5. Entry point </h4>

The entry point is:
```python
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated. Turning off all pixels...")
        clear_pixels()
```

This ensures the script only runs when executed directly, terminates when the script is not run properly.

---

<h3> Midi pad: </h3>
<h4> 1. Setup </h4>
MIDI CONNECTIONS:

- `inport`: Listens for MIDI **button press input** from the Launchpad.
- `outport`: Sends MIDI **lighting commands** to the Launchpad.

COLOR MAP: A dictionary maps color names to MIDI velocity values:
```python
COLOR_MAP = {
    'red': 5,
    'green': 21,
    'blue': 78,
    'yellow': 13,
    'off': 0,
    'flash': 5
}
```

<h4>2. Grid mapping</h4>

- An 8×8 grid (`launchpad_grid`) is created using MIDI note numbers.
- Top-left is note **81**, going right adds 1, going down subtracts 10.

<h4>3. Helper functions</h4>

### get_2x2_block(x, y)
Returns a list of 4 MIDI notes forming a 2×2 square starting at `(x, y)`.
### clear()
Turns off all LEDs by sending `velocity=0` to every note.
### light_block(block, color)
Lights up all notes in the given `block` with the specified `color`.
### flash_red()
Flashes the entire grid red briefly as a warning for incorrect input.

<h4>3. Game setup</h4>

- Divides the 8×8 grid into non-overlapping 2×2 blocks.
- Randomly assigns:
  - 4 red blocks
  - 4 green blocks
  - 4 blue blocks
  - 4 yellow blocks

```python
{
  'red': [block1, block2, ...],
  'green': [...],
  ...
}
```

<h4>4. Main game loop</h4>

1. Clear the board.
2. Generate and light up 16 colored blocks.
3. Randomize a color sequence of 16 steps (4 of each color).
4. Wait for player input:
   - On pad press:
     - Identify the pressed block’s color.
     - Compare it with the expected color in the sequence.
     - If correct: turn off the block and move to the next.
     - If incorrect: flash red and restart.
5. Repeat when the sequence is completed or failed.

<h4>5. Entry Point</h4>

At the end of the script, the Python entry point check is:
```python
if __name__ == "__main__":
    run_game()
```

This ensures the game starts only when the script is run directly.

---
<h3>Push Button:</h3>
<h4>1: Set-up</h4>

Importing function and values from midi.py:

```python
from midi import *
```

Pin Setup:

```python
button_pin = 17  # If the button is on GPIO 17
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button pin set as input w/ pull-up
```

<h4>2: Toggle Function</h4>

```python
toggle = 0  # Variable to toggle between 0 and 1

# This function will be called when the button is pressed
def button_callback(channel):
    global toggle
    toggle = 1 - toggle  # Toggle the value
    if toggle == 1:
        start()
        print("Toggle On!")
        
    if toggle == 0: 
        stop()
        print("Toggle off.")
```
When the button is pressed, it will change the toggle value to 1 or 0.<br>
1 being for on, 0 being for off

<h5>Functions:</h5>

Start()

```python
def start():
    os.system("sudo ~/egl314/bin/python ledon.py") # Executes ledon.py
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=COLOR_MAP['flash'])) # Turns all grids on the Launchpad red, values imported from midi.py
```

ledon.py contains a function to turn all the led on the Neopixel white

ledon.py

```python
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 240, 200)) # Sets all the led to white
strip.show()
```

---

Stop()

```python
def stop():
    os.system("sudo ~/egl314/bin/python ledoff.py") # Executes ledoff.py 
    clear() # Imported Function from midi.py
```

ledoff.py contains a function to turn all the led off

ledoff.py

```python
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 0)) # Sets all the led to off
strip.show()
```

---

Clear()

```python
def clear():# Turns all the pads off by sending velocity=0 to all notes.
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=0))
```

<h4>3: Loop</h4>

```python
try:
    print("Press the button to turn on or off.")
    while True:
        # Main loop does nothing, just waits for button events
        time.sleep(0.1)
except KeyboardInterrupt:
    # Clean up GPIO on CTRL+C exit
    GPIO.cleanup()
```

Loops the script.



