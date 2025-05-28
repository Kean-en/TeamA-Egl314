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

# Define the four colors
COLORS = {
    'red': Color(255, 0, 0),     # Red
    'green': Color(0, 255, 0),   # Green
    'yellow': Color(128, 51, 0), # Yellow
    'brown': Color(40, 10, 0)    # Brown
}

def clear_pixels():
    """Turn off all pixels"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def signal_handler(sig, frame):
    """Handle Ctrl+C to clean up before exiting"""
    print("\nProgram terminated. Turning off all pixels...")
    clear_pixels()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def display_sequence(color_sequence):
    """Display a sequence of colors evenly across the strip"""
    num_colors = len(color_sequence)
    pixels_per_color = LED_COUNT // num_colors
    remainder = LED_COUNT % num_colors

    print(f"\nDisplaying sequence: {', '.join(color_sequence)}")
    print(f"Using {pixels_per_color} pixels per color with {remainder} extra pixels at the end")

    pixel_index = 0
    for i, color_name in enumerate(color_sequence):
        if color_name.lower() in COLORS:
            color = COLORS[color_name.lower()]
            if i == num_colors - 1:
                segment_pixels = pixels_per_color + remainder
            else:
                segment_pixels = pixels_per_color

            for j in range(segment_pixels):
                if pixel_index < LED_COUNT:
                    strip.setPixelColor(pixel_index, color)
                    pixel_index += 1
        else:
            print(f"Warning: Color '{color_name}' not found. Skipping.")

    strip.show()

def get_color_value(prompt):
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= 255:
                return value
            else:
                print("Please enter a value between 0 and 255")
        except ValueError:
            print("Please enter a valid number")

def main():
    print("=== NeoPixel WS2812B Color Sequence Test Demo (Using rpi_ws281x) ===")
    print(f"Configured for {LED_COUNT} pixels on GPIO pin {LED_PIN}")

    print("\nAvailable colors:")
    for color in sorted(COLORS.keys()):
        print(f"- {color}")

    while True:
        print("\nOptions:")
        print("1. Enter custom color sequence")
        print("2. Turn off all pixels and exit")
        print("3. Flashbang")
        print("4. RGB Test")
        print("5. Randomiser (random color sequence, no repeats)")

        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            input_sequence = input("\nEnter color sequence (comma-separated, e.g., red,green,yellow,brown): ")
            color_sequence = [color.strip().lower() for color in input_sequence.split(',')]

            invalid_colors = [color for color in color_sequence if color not in COLORS]
            if invalid_colors:
                print(f"Warning: These colors are not recognized: {', '.join(invalid_colors)}")
                print("Available colors: " + ", ".join(sorted(COLORS.keys())))
                continue

            display_sequence(color_sequence)

        elif choice == '2':
            print("Turning off all pixels and exiting...")
            clear_pixels()
            break

        elif choice == '3':
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(255, 240, 200))
            strip.show()
            print("Flashbang!")

        elif choice == '4':
            red = get_color_value("Enter red component (0-255): ")
            green = get_color_value("Enter green component (0-255): ")
            blue = get_color_value("Enter blue component (0-255): ")

            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(red, green, blue))
            strip.show()

        elif choice == '5':
            colors = list(COLORS.keys())
            random.shuffle(colors)
            print("Randomised color sequence:")
            print(", ".join(colors))
            input("Press Enter to confirm and display this sequence...")
            display_sequence(colors)

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

if _name_ == "_main_":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated. Turning off all pixels...")
        clear_pixels()