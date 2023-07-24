#!/usr/bin/python3
from time import time, sleep
from numpy import save
from math import floor
import threading
from struct import unpack_from
import subprocess

try:
    from Sensors.gpsModule import ubx, gps_io
    from Sensors.Log import Log
except:
    from gpsModule import ubx, gps_io
    from Log import Log


class Gps:


    def __init__(self, Write_Directory, log_file): #runs upon initialization
        self.wd = Write_Directory
        self.log = Log("GPS:", log_file)
        self.threads = []
        self.gpsio = gps_io(input_speed=38400)
        self.ih = ubx.ubx()
        self.ih.io_handle = self.gpsio
        self.name = "GPS"
        self._is_calibrated = False
        self.is_calibrating = False

    
    @property
    def is_calibrated(self):
        if self.is_calibrating or self._is_calibrated == False:
            return False

        # gps was previously calibrated successfully, but will check again anyways
        is_cal_thread = threading.Thread(target=self.is_calibrated_run , args=())
        is_cal_thread.start()
        return self._is_calibrated

    def is_calibrated_run(self):
        t0 = time()
        
        while time() < t0 + 0.15: # should be enough time to recieve 1-2 epochs
            out = self.gpsio.ser.sock.recv(8192)

            # check if first 4 bytes in message match header of UBX-NAV-PVT
            if b'\xb5b\x01\x07' in out[0:4]:
                nums = unpack_from('<LHBBBBBBLlBBBBllllLLlllllLLHHHH', out[6:], 0)
                #                                            trim header ^^
                fix_type = self.fix_types[nums[10]] # fix type is the 11th number in array
                if fix_type == 3:
                    self._is_calibrated = True
                    return

        self._is_calibrated = False  # if got no pvt message / no fix then gps is no longer calibrated
        self.kill_all_threads() # stop threads from recieving false data
       

    def calibrate(self):
        self.is_calibrating = True
        cal_thread = threading.Thread(target=self.run_calibrate, args=())
        cal_thread.start()
        self.log("beginning calibration")

    fix_types = {
        0 : "no fix",
        1 : "dead reckoning",
        2 : "2d fix",
        3 : "3d fix",
        4 : "GNSS + dead reckoning",
        5 : "time only"
    }

    def run_calibrate(self):
        # 0. ensure binary protocol
        self.log("Checking protocol")
        while True:
            out = []

            # hopefully 30 messages is enough to capture both NMEA 
            # and ubx messages if they are being outputted
            for i in range(30):
                
                out += [self.read()]

            
            binary_prot = False
            NMEA_prot = False
            for line in out:
                strout= str(line[:1])
                
                if "$" in strout:
                    NMEA_prot = True
                if "\\x" in strout:
                    binary_prot = True
            if binary_prot and not NMEA_prot:
                break

            # debug checks
            if binary_prot:
                self.log("outputting ubx protocol")
            else: #if not enabled, enable it
                self.log("Enabling binary protocol")
                subprocess.run(['ubxtool', '-e', 'BINARY', '-w', '0'])

            if NMEA_prot:
                self.log("outputting NMEA protocol, disabling")
                subprocess.run(['ubxtool', '-d', 'NMEA', '-w', '0'])
            sleep(5)
        self.log("outputting proper protocol")

        # see ubx interface desciption for more codes
        #          class ID 
        # NAV EOE = 0x01 0x61 = 97
        # NAV PVT = 0x01 0x07
        # NAV SAT = 0x01 0x35 = 53

        # TODO: ensure 20hz sample rate


        # 1. Wait for fix
        no_fix = True
        fix_type = None
        self.log("Checking fix")
        # doesnt hurt to reenable messages
        # c = class
        # i = id
        # r = rate, ie output message every r epochs
        # an epoch is roughly the same as a timestep. 
        # rate of epoch should be 20hz and each epoch 
        # it should output a pvt and eoe msg, and every 
        # 5th epoch a sat msg.
        #                                     --- c i r ---
        subprocess.run(['ubxtool', '-p', 'CFG-MSG,1,7,1', '-w', '0'])
        subprocess.run(['ubxtool', '-p', 'CFG-MSG,1,97,1', '-w', '0'])
        subprocess.run(['ubxtool', '-p', 'CFG-MSG,1,53,5', '-w', '0'])
        while no_fix:
            out = self.read()

            # TODO: add timeout if no pvt message for too long
            t0 = time()
            if time() > t0 + 10:
                if pvt_flag:
                    self.log("10s with no fix")
                    pvt_flag=False
                else:
                    self.log("no PVT message in 10s")
                    subprocess.run(['ubxtool', '-p', 'CFG-MSG,1,7,1', '-w', '0'])


            # check if first 4 bytes in message match header of UBX-NAV-PVT
            if b'\xb5b\x01\x07' in out[0:4]:
                pvt_flag=True

                nums = unpack_from('<LHBBBBBBLlBBBBllllLLlllllLLHHHH', out[6:], 0)
                #                                            trim header ^^

                # for debugging, shows what each number corresponds to
                #s = ('  iTOW %u time %u/%u/%u %02u:%02u:%02u valid x%x\n'
                #    '  tAcc %u nano %d fixType %u flags x%x flags2 x%x\n'
                #    '  numSV %u lon %d lat %d height %d\n'
                #    '  hMSL %d hAcc %u vAcc %u\n'
                #    '  velN %d velE %d velD %d gSpeed %d headMot %d\n'
                #    '  sAcc %u headAcc %u pDOP %u reserved1 %u %u %u' % nums)
                
                fix_type = self.fix_types[nums[10]]
            
            if fix_type == "3d fix":
                no_fix = False
                #print("GPS has 3d fix")
            else:
                #print("GPS has", fix_type)
                pass
        self.log("has " + fix_type)

        
        # 2. ensure pps signal (OPTIONAL???)
        # mangling output of 'ifconfig wlan0' to get the item I want to check. if UP is in flags, wifi is enabledi
        try:
            wifi_en = 'UP' in str(subprocess.check_output(['ifconfig', 'wlan0'])).split('\n')[0].split()[1]
        except:
            wifi_en = None

        if wifi_en:
            self.log("connected to internet, will not use pps signal unless connection drops")
        else:
            t0 = time()

            wait_time = 60
            self.log("GPS: waiting for pps signal sync")
            self.log("will wait only " + str(wait_time) +" seconds") 
            pps_status = None
            while (str(pps_status) != "b\'#*\'") and (time() - t0 > wait_time):
                # compares current pps status to "being used" code
                # exits if pps is being used
                # below command runs 'chronyc sources' and strips output for code
                # couldn't find a better way to check if pps is being used
                try:
                    pps_status = subprocess.check_output(['chronyc', 'sources', '|', 'grep', 'PPS0']).split()[10]
                except Exception as e:
                    self.log("error checking chrony sources")

                sleep(2)
                self.log("valid pps signal")

        self.log("has been calibrated")
        self._is_calibrated = True
        self.is_calibrating = False

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

        self.log.write("GPS: all threads killed")

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
        while True:
            print(self.read())
            self.ih.decode_msg(self.read())

if __name__ == "__main__":
    
    with open("/home/fissellab/BVEXTracker/Logs/GpsLog", "a") as log:
        test = Gps("/home/fissellab/BVEXTracker/output/GPS/", log)

        #test.calibrate()
        #while not test.is_calibrated:
        #    sleep(1)
        test.test()
    



