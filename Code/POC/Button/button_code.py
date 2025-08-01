import RPi.GPIO as GPIO
import time
import os

# Pin Setup:
button_pin = 15  # Assuming you connected the button to GPIO 15
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button pin set as input w/ pull-up

toggle = 0  # Variable to toggle between 0 and 1

# This function will be called when the button is pressed
def button_callback(channel):
    global toggle
    toggle = 1 - toggle  # Toggle the value
    if toggle == 1:
        print("Game On!")
        os.system("sudo ~/egl314/bin/python GameFinal.py")

    if toggle == 0: 
        os.system("sudo ~/egl314/bin/python ledoff.py")
        print("Game off.")



# Detect a rising edge event on the button pin, and debounce it with 300ms to avoid false triggers
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    print("Press the button to turn on or off.")
    while True:
        # Main loop does nothing, just waits for button events
        time.sleep(0.1)
except KeyboardInterrupt:
    # Clean up GPIO on CTRL+C exit
    GPIO.cleanup()

GPIO.cleanup()  # Clean up GPIO on normal exit
