import RPi.GPIO as GPIO
import threading
from time import sleep

try:
    from Log import Log
except:
    from Sensors.Log import Log


class LED:
    def __init__(self, log_file):
        self.mode = 0 # mode will correspond to number of sensors currently collectin data
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
        self.log = Log("LED:", log_file)
        thread = threading.Thread(target=self.run, args=())
        self.thread = thread
        thread.start()
        self.log("initialized, thread running")

    def run(self): #reads the mode out in binary on the LED
        try:
            while True:
                temp_mode = self.mode
                assert temp_mode <= 5 #only 5 sensors, should not get number bigger than this
                for i in range(temp_mode):
                    GPIO.output(18, GPIO.HIGH)
                    sleep(0.2)
                    GPIO.output(18, GPIO.LOW)
                    sleep(0.2)

                GPIO.output(18, GPIO.LOW)
                sleep(1)
                # flash on/off rapidly to show is operating still
        except Exception as e:
            self.log(str(e))


if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/Logs/ledLog", "a") as f:

        led = LED(f)


        led.mode = 1
        sleep(2)
        led.mode = 2
        sleep(2)
        led.mode = 3
        sleep(2)
        led.mode = 4
        sleep(2)
        led.mode = 5
        sleep(2)
