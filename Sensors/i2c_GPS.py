#!/usr/bin/python3
from time import time, sleep
from numpy import save
from math import floor
import threading
import struct
import subprocess
import multiprocessing as mp
import smbus

i2c_bus = 1
GPS_ADDRESS = 0x42
BYTES_AVAIL_HIGH_REG = 0xFD
BYTES_AVAIL_LOW_REG = 0xFE
READ_STREAM_REG = 0xFF

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
        self.ih = smbus.SMBus(1)
        self.is_calibrated = True
        self.is_calibrating = False
        self.log("initialized")
        sleep(1)
        
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

        while not flag.is_set():
            try: 
                byte_dat = (self.ih.read_byte_data(GPS_ADDRESS, READ_STREAM_REG)).to_bytes(1, byteorder='little')
                if recv_bytes > 0:
                    recv_bytes -= 1
                    buff += byte_dat
                
                if possible_start:
                    possible_start = False
                    if byte_dat == b'b':  # marks start of new message transmission
                        recv_bytes = 98 # recv another xx bytes of data into buffer
                        buff = struct.pack("<d", time()) + buff
                        file.write(buff)

                        buff = b'\xb5b' # add this to buffer as it wasnt added previously

                if byte_dat == b'\xb5' and recv_bytes == 0:
                    #print("possible start")
                    possible_start = True
            except IOError:
                self.log("error reading i2c gps address, trying again in 10s")
                sleep(10)        
            except Exception as e:
                self.log("error: " + str(e))
                break

        file.close()
        self.log("process finished")


    def read_file(self, f):

        #gpsio = gps_io(input_file_name=file_name, read_only=True, write_requested=False, gpsd_host=None)
        f.read(8)
        while True:
            try:
                bin_dat = f.read(108)
                #print(bin_dat, "\n\n")
                time_bin_dat = bin_dat[0:8]
                nav_pvt_bin = bin_dat[8:108]
                #print(nav_pvt_bin)
                print(self.checksum(nav_pvt_bin, 100), int(nav_pvt_bin[-2]), int(nav_pvt_bin[-1]))
                u = struct.unpack_from('<LHBBBBBBLlBBBBllllLLlllllLLHHHH', nav_pvt_bin[6:90], 0)
                print("\n\n")
                s = ('  iTOW %u time %u/%u/%u %02u:%02u:%02u valid x%x\n'
                     '  tAcc %u nano %d fixType %u flags x%x flags2 x%x\n'
                     '  numSV %u lon %d lat %d height %d\n'
                     '  hMSL %d hAcc %u vAcc %u\n'
                     '  velN %d velE %d velD %d gSpeed %d headMot %d\n'
                     '  sAcc %u headAcc %u pDOP %u reserved1 %u %u %u' % u)
                print(s)
            except Exception as e:
                print(e)
                break

    def checksum(self, msg, m_len):
        """Calculate u-blox message checksum"""
        # the checksum is calculated over the Message, starting and including
        # the CLASS field, up until, but excluding, the Checksum Field:

        ck_a = 0
        ck_b = 0
        for c in msg[0:m_len]:
            ck_a += c
            ck_b += ck_a

        return [ck_a & 0xff, ck_b & 0xff]

if __name__ == "__main__":
    
    with open("/home/fissellab/BVEXTracker/Logs/GpsLog", "a") as log:
        test = Gps("/home/fissellab/BVEXTracker/output/i2c_GPS/", log)
        with open("/home/fissellab/BVEXTracker/output/i2c_GPS/1691767125", "rb") as f:
            test.read_file(f)



