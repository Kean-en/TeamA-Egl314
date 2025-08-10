# Introduction

<br>

This section documents the game logic that handles MIDI input/output for the **Launchpad Pro MK3** and RGB LED control using **NeoPixel** on a **Raspberry Pi**.

<br><br>

The game uses:
<br>

* Two *Launchpad Pro MK3* devices for interactive feedback (via MIDI)  
* A *NeoPixel* LED strip for visual feedback  
* GPIO button input for game start/stop control  
<br><br>

# NeoPixel Setup and Functions
### Strip Configuration
```
python
from rpi_ws281x import Color, Adafruit_NeoPixel

LED_COUNT = 120
LED_PIN = 18
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN)
```
* LED_COUNT: Number of LEDs in the strip.
 * LED_PIN: GPIO pin used to control the strip.
 <br>

 ### Initialize the Strip
 ```
strip.begin()

```
This is called once during game setup to start communication with the strip.
<br>

### Function: show_color(color)
 ```
def show_color(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


```
* Lights up the entire NeoPixel strip with a given Color(R, G, B).
* Used to give visual cues (e.g., green = ready, red = stop).

### Function: clear_pixels()
```
def clear_pixels():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


```
* Turns off all LEDs on the strip.
<br>

# MIDI Launchpad Logic
### Setup
```
import mido

MIDI_PORTS = [
    "Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0",
    "Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 32:0"
]
outports = [mido.open_output(p) for p in MIDI_PORTS]



```
* Opens two Launchpad Pro MK3 MIDI outputs.
* The ports in this example 28:0 and 32:0 are 2 seperate midis each with different ports

### Check Midi Ports
```
import mido

print("Available MIDI Input Ports:")
for port in mido.get_input_names():
    print(f" - {port}")

print("\nAvailable MIDI Output Ports:")
for port in mido.get_output_names():
    print(f" - {port}")


```
This is a code that should be run seperately in order to check for the midi ports. It should give the following outcome 
```
Available MIDI Input Ports:
 - LPProMK3 MIDI 0
 - LPProMK3 MIDI 2

Available MIDI Output Ports:
 - LPProMK3 MIDI 1
 - LPProMK3 MIDI 3



```
### Function: clear_launchpad()
```
def clear_launchpad():
    for outport in outports:
        for note in range(0, 128):
            outport.send(mido.Message('note_on', note=note, velocity=0))


```
* Turns off all pad lights on both Launchpads by sending note_on with velocity=0.

# Button Control Logic (GPIO)
```
import RPi.GPIO as GPIO

BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

```
* Sets up GPIO 17 with a pull-up resistor to detect button presses.
### Function: stop_game()
```
def stop_game():
    print("[Game Paused] Game is now stopped.")
    show_color(Color(255, 0, 0))  # Red
    clear_launchpad()
    clear_pixels()
    wait_for_button_hold()


```
* Pauses the game and waits for a new hold to resume.
### Function: monitor_stop()
```
def monitor_stop():
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            start_time = time.time()
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                if time.time() - start_time >= 4:
                    stop_game()
                time.sleep(0.1)
        time.sleep(0.1)
```
* Runs in a background thread to detect 4-second hold to pause the game.

### Function: wait_for_button_hold()
```
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
                print("[OSC] LIGHT: Go+ Sequence 56")
                LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 56")
                strip_color_off()
                return
        else:
            # Reset if released early
            hold_start = None
            strip_color_off()

        time.sleep(0.01)
```
* Waits for 2-second button hold to begin the game.
* Provides live color feedback:
    * Green = ready
    * Off = Did not hold for 2s

# Main Game Loop
### Game Entry Point
```
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Game interrupted by user.")
        clear_launchpads()
        strip_color_off()
        GPIO.cleanup()
        exit(0)

```

### main() Function
```
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


```
* Starts game only after 2-second button press hold.
* Continuously runs level logic until paused.
* Cleans up gracefully and ends the code when Ctrl+C is pressed in terminal.

<br>

# Summary


|**Component**|**Purpose**|**Key Functions**|
|--------|--------|:--------:|
|NeoPixel LED  |Visual Feedback |show_color(), clear_pixels()  |
|Launchpad MIDI   |Pad light control  |	clear_launchpad(), main()  |
|GPIO Button   |Start/stop input  |wait_for_button_hold(), monitor_stop() |
|Threads   |	Stop game detection  |monitor_stop() |




# Notes
* Do not unplug Launchpad while game is running.( this will change the ports)
* Hold time to start = 2 seconds.
* Hold time to stop = 4 seconds.
* LED feedback is always used to show the game's state.