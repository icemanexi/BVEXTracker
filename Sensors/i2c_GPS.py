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
        possible_start = False
        byte_dat = None
        buff = b''
        recv_bytes = 0

        try:
            while not flag.is_set():

                byte_dat = (bus.read_byte_data(GPS_ADDRESS, READ_STREAM_REG)).to_bytes(1, byteorder='little')
                if recv_bytes > 0:
                    recv_bytes -= 1
                    buff += byte_dat
                
                if possible_start:
                    possible_start = False
                    if byte_dat == b'b':  # marks start of new message transmission
                        recv_bytes = 98 # recv another xx bytes of data into buffer
                        print(buff)
                        ubxt.decode_msg(buff)

                        buff = b'\xb5b' # add this to buffer as it wasnt added previously

                if byte_dat == b'\xb5' and recv_bytes == 0:
                    #print("possible start")
                    possible_start = True

        except Exception as e:
            self.log("error wrile running GPS: " + str(e))
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
        return 


if __name__ == "__main__":
    
    with open("/home/fissellab/BVEXTracker/Logs/GpsLog", "a") as log:
        test = Gps("/home/fissellab/BVEXTracker/output/GPS/", log)

        test.new_thread()
