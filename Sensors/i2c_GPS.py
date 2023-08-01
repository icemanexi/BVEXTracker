#!/usr/bin/python3

from time import time, sleep
from numpy import save
from math import floor
import threading
from struct import unpack_from
import subprocess


try:
    from gpsModule import ubx, gps_io
    from Log import Log
except:
    from Sensors.gpsModule import ubx, gps_io
    from Sensors.Log import Log


class Gps:
    def __init__(self, Write_Directory, log_file): #runs upon initialization
        self.wd = Write_Directory
        self.log = Log("GPS:", log_file)
        self.threads = []
        self.name = "GPS"

    
    @property
    def is_calibrated(self):
        return 

    def is_calibrated_run(self):
        return

    def calibrate(self):
        return

    def run_calibrate(self):
        return

    def new_thread(self):
        stop_flag = threading.Event()
        thread = threading.Thread(target=self.run, args=(stop_flag,))
        self.threads.append({"thread" : thread, "stop flag" : stop_flag, "start time" : time()})
        thread.start()
        sleep(0.003)
        self.log("thread started")
        if len(self.threads) == 2:
            prevThreadDict = self.threads.pop(0)
            prevThreadDict["stop flag"].set()
        if len(self.threads) > 2:
            self.log("Something went wrong with the threading in gps!")

    def kill_all_threads(self):
        for t in self.threads:
            t["stop flag"].set()

        self.log("all threads killed")

    def run(self, flag):
        file = open(self.wd + str(floor(time())), "wb+")

        try:
            while not flag.is_set():
                file.write(self.read())
        except Exception as e:
            self.log("error wrile running GPS: ", e)
            file.close()

        file.close()
        self.log("thread finished")


    def read_file(self, file_name : str):
        assert file_name is str # File name needs to be string
        data = []
        gpsio = gps_io(input_file_name=file_name, read_only=True, write_requested=False, gpsd_host=None)
        while True:
            # this function will print the data to screen, but will not return it
            gpsio.read(decode_func=self.ih.decode_msg)

    def test(self):
        out = None
        while True:
            out = self.gpsio.ser.sock.recv(8192)
            print(out)
            self.ih.decode_msg(out)

if __name__ == "__main__":
    
    with open("/home/fissellab/BVEXTracker/Logs/GpsLog", "a") as log:
        test = Gps("/home/fissellab/BVEXTracker/output/GPS/", log)

        test.test()
        #test.calibrate()
        #while not test.is_calibrated:
        #    sleep(1)
        t0 = time()
        while time() < t0 + 30:
            try:
                if not test.is_calibrated:
                    if not test.is_calibrating:
                        test.calibrate()
                    continue
                if len(test.threads) == 0:
                    test.new_thread()
                elif time() - test.threads[0]["start time"] > 10:
                    test.new_thread()
            except Exception as e:
                print(e)
            sleep(2)
