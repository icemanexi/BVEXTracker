#!/usr/bin/python3

from time import time, sleep
from numpy import save
from math import floor
import multiprocessing as mp
from struct import unpack_from
import subprocess
import smbus


try:
    from gpsModule import ubx, gps_io
    from Log import Log
except:
    from Sensors.gpsModule import ubx, gps_io
    from Sensors.Log import Log


class Gps:
    def __init__(self, Write_Directory, log_file): #runs upon initialization
        self.wd = Write_Directory
        self.log = Log("i2c GPS:", log_file)
        self.processes = []
        self.name = "i2c GPS"
        self.error_timer = 0        
        self.ih = smbus.SMBus(1) # i2c_bus = 1
        sleep(1)

        self.log("i2c GPS initialized")
    
    @property
    def is_calibrated(self):
        return True

    def is_calibrated_run(self):
        return

    def calibrate(self):
        return True

    def run_calibrate(self):
        return

    def new_process(self):
        stop_flag = mp.Event()
        process = mp.Process(target=self.run, args=(stop_flag,))
        self.processes.append({"process" : process, "stop flag" : stop_flag, "start time" : time()})
        process.start()
        sleep(0.003)
        self.log("process started")
        if len(self.processes) == 2:
            prevProcessDict = self.processes.pop(0)
            prevProcessDict["stop flag"].set()
        if len(self.processes) > 2:
            self.log("Something went wrong with the processing in gps!")

    def kill_all(self):
        for t in self.processes:
            t["stop flag"].set()

        self.log("all processes killed")

    def run(self, flag):
        file = open(self.wd + str(floor(time())), "wb+")
        possible_start = False
        byte_dat = None
        buff = b''
        recv_bytes = 0
        GPS_ADDRESS = 0x42
        READ_STREAM_REG = 0xFF

        try:
            while not flag.is_set():

                byte_dat = (self.ih.read_byte_data(GPS_ADDRESS, READ_STREAM_REG)).to_bytes(1, byteorder='little')
                if recv_bytes > 0:
                    recv_bytes -= 1
                    buff += byte_dat
                
                if possible_start:
                    possible_start = False
                    if byte_dat == b'b':  # marks start of new message transmission
                        recv_bytes = 98 # recv another xx bytes of data into buffer
                        pack = struct.pack("<d", time()) + buff  # store time then the msg buffer
                        file.write(pack)
                        ubxt.decode_msg(buff)  # for debugging

                        buff = b'\xb5b' # add this to buffer as it wasnt added previously

                if byte_dat == b'\xb5' and recv_bytes == 0:
                    #print("possible start")
                    possible_start = True

        except Exception as e:
            if time() - self.error_timer > 10: # only output erors every 10s             
                self.log("error wrile running GPS: " + str(e))
                self.error_timer = time()
                
            file.close()

        file.close()
        self.log("process finished")


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

        test.new_process()
