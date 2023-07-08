from time import time, sleep
import threading
from GPS import Gps

class test:
    def __init__(self):
        print("test init")

    def thread_test(self):
        thread = threading.Thread(target=self.run, args=())
        thread.start()

    def run(self):
        for i in range(10):
            print("weewoo")
            sleep(1)


gps = Gps("/home/fissellab/BVEXTracker-main/output/GPS/")
t = test()

gps.calibrate()
t.thread_test()





