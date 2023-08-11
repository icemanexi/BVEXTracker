#!/usr/bin/python3
from time import time, sleep
from numpy import save
from math import floor
import multiprocessing as mp
import struct
import subprocess
import gpsd

try:
    from gpsModule import ubx, gps_io
    from Log import Log
except:
    from Sensors.gpsModule import ubx, gps_io
    from Sensors.Log import Log


class Gps:
    def __init__(self, Write_Directory, log_file): #runs upon initialization
        self.wd = Write_Directory
        self.log = Log("ser GPS:", log_file)
        self.processes = []
        self.gpsio = gps_io(input_speed=38400)
        self.ih = ubx.ubx()
        self.ih.io_handle = self.gpsio
        self.name = "serial GPS"
        self._is_calibrated = False
        self.is_calibrating = False
        gpsd.connect()

    
    @property
    def is_calibrated(self):
        return True
        if self.is_calibrating or self._is_calibrated == False:
            return False

        # gps was previously calibrated successfully, but will check again anyways
        is_cal_process = mp.Process(target=self.is_calibrated_run , args=())
        is_cal_process.start()

        return self._is_calibrated

    def is_calibrated_run(self):
        return True # FIXME: not currently working ovo
        t0 = time()
        
        while time() < t0 + 1: # should be enough time to recieve 1-2 epochs
            out = self.gpsio.ser.sock.recv(8192)

            # check if first 4 bytes in message match header of UBX-NAV-PVT
            self.log(str(out))
            if b'\xb5b\x01\x07' in out[0:6]:
                self.log("passed if")
                nums = strcut.unpack_from('<LHBBBBBBLlBBBBllllLLlllllLLHHHH', out[6:], 0)
                #                                            trim header ^^
                fix_type = self.fix_types[nums[10]] # fix type is the 11th number in array
                if fix_type == 3:
                    self._is_calibrated = True
                    return

        self.log("was calibrated but now isnt...")
        self._is_calibrated = False  # if got no pvt message / no fix then gps is no longer calibrated
        self.kill_all() # stop processes from recieving false data
       

    def calibrate(self):
        return 
        self.is_calibrating = True
        cal_process = mp.Process(target=self.run_calibrate, args=())
        self.log("beginning calibration")
        cal_process.start()

    def run_calibrate(self):
        #-1. check if gps is outputting
        t0 = time()
        while True:
            strout = str(self.gpsio.ser.sock.recv(8192))
            if "$" in strout or "\\x" in strout:
                self.log("recieving output from gps")
                break
            elif time() > t0 + 10:
                # output this message every 10s
                t0 = time()
                self.log("not recieving output from gps") 

        # 2. ensure pps signal (OPTIONAL???)
        t0 = time()

        #wait_time = 60
        #self.log("GPS: waiting for pps signal sync")
        #self.log("will wait only " + str(wait_time) +" seconds") 
        #pps_status = None
        #while (str(pps_status) != "b\'#*\'") and (time() - t0 > wait_time):
        #    # compares current pps status to "being used" code
        #    # exits if pps is being used
        #    # below command runs 'chronyc sources' and strips output for code
        #    # couldn't find a better way to check if pps is being used
        #    try:
        #        pps_status = subprocess.check_output(['chronyc', 'sources', '|', 'grep', 'PPS0']).split()[10]
        #    except Exception as e:
        #        self.log("error checking chrony sources")

        #    sleep(2)
        #    self.log("valid pps signal")

        self.log("has been calibrated")
        self._is_calibrated = True
        self.is_calibrating = False

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

        try:
            while not flag.is_set():
                packet = gpsd.get_current()
                if packet.mode >= 3:
                    t = time()
                    bin_dat = struct.pack("<dfffff", t, packet.lat, packet.lon, packet.alt, packet.speed(), packet.track)
                    file.write(bin_dat)
                else:
                    self.log("no fix")
                    sleep(10)
                sleep(1)
        except Exception as e:
            self.log("error wrile running GPS: " + str(e))
            file.close()

        file.close()
        self.log("process finished")

    def read(self):
        out = None
        while out == None:
            out = self.gpsio.ser.sock.recv(8192)
        return out

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
        test = Gps("/home/fissellab/BVEXTracker/output/ser_GPS/", log)
        f = mp.Event()
        test.run(f)
        sleep(10)
        f.set()

