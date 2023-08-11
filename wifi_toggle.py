import RPi.GPIO as GPIO 
import process
import time

GPIO_PIN = 40

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    try:
        if GPIO.input(GPIO.PIN) == GPIO.HIGH:
            disable_wifi()
        else:

