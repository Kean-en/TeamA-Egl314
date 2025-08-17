import time
from rpi_ws281x import PixelStrip, Color
from threading import Thread, Event
import RPi.GPIO as GPIO
from pythonosc import udp_client

# LED Config
LED_COUNT = 120
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
CHANNEL = 0
LIGHT_CLIENT = udp_client.SimpleUDPClient("192.168.254.213", 2000)
PI_A = "192.168.254.51"
PI_B = "192.168.254.49"
PI_Addr = "/print"
PI_PORT = "2629"

# Button Config
BUTTON_PIN = 17  # Connect one side to GPIO 17, the other to GND

# Global variables
strip = None
animation_thread = None
stop_animation = Event()

def initialize():
    """Initialize the NeoPixel strip and GPIO"""
    global strip
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                           LED_INVERT, LED_BRIGHTNESS, channel=CHANNEL)
        strip.begin()
        print(f"NeoPixel strip initialized: {LED_COUNT} pixels on pin {LED_PIN}")
        return True
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return False

def cleanup():
    """Clean up NeoPixel and GPIO resources"""
    global animation_thread, stop_animation

    stop_animation.set()
    if animation_thread and animation_thread.is_alive():
        animation_thread.join(timeout=1)

    if strip:
        clear_strip()

    GPIO.cleanup()
    print("Cleanup complete")

def rgb(r, g, b):
    return Color(int(r), int(g), int(b))

def clear_strip():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, rgb(0, 0, 0))
    strip.show()

def stop_current_animation():
    global stop_animation, animation_thread
    stop_animation.set()
    if animation_thread and animation_thread.is_alive():
        animation_thread.join(timeout=1)
    stop_animation.clear()

def white_loading_wave_pulses(pulses=1, speed=1.5):
    """
    Show exactly `pulses` of white wave animation moving left to right.
    `speed`: how many pulses per second.
    """
    def wave_animation():
        fps = 60
        duration = pulses / speed
        total_frames = int(duration * fps)

        for frame in range(total_frames):
            if stop_animation.is_set():
                break
            t = frame / fps
            wave_pos = (t * speed * LED_COUNT) % LED_COUNT
            for i in range(strip.numPixels()):
                distance = abs(i - wave_pos)
                brightness = max(0, 255 - distance * 30)
                strip.setPixelColor(i, rgb(brightness, brightness, brightness))
            strip.show()
            time.sleep(1 / fps)

        clear_strip()

    stop_current_animation()
    global animation_thread
    animation_thread = Thread(target=wave_animation, daemon=True)
    animation_thread.start()

def button_callback(channel):
    if not animation_thread or not animation_thread.is_alive():
        white_loading_wave_pulses(pulses=1, speed=1.5)  # <<< adjust speed here if needed

if __name__ == "__main__":
    if initialize():
        try:
            GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
            print("Press the button to trigger 1 wave pulse.")
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            cleanup()
