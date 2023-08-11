from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import multiprocessing as mp
from math import floor
import struct

try:
    from adafruit_lis3mdl import LIS3MDL, Rate
    from Log import Log
except:
    from Sensors.adafruit_lis3mdl import LIS3MDL, Rate
    from Sensors.Log import Log

class Magnetometer:
    def __init__(self, Write_Directory, log_file):
        self.wd = Write_Directory
        self.log = Log("MAG:", log_file)
        self.processes = []
        try:
            self.ih = LIS3MDL(I2C(1))
        except ValueError as e:
            self.log("IO error: " + str(e))

        self.header = ("time", "mag x", "mag y", "mag z")
        self.name = "Magnetometer"

        """ 
        not super sure how the magnetometer calibration works, but I think the
        way that it's done now can be done in post so for ease of setup, there
        will not be a calibration script on startup

        """
        self.is_calibrated = True
        self.is_calibrating = False

        self.log("initialized")

#------------------------------calibration---------------------------------

    def calibrate(self):
        self.is_calibrating = True
        self.log("calibration process started")
        cal_proc = mp.Process(target = self.run_calibrate, args=())
        cal_proc.start()
        

    def run_calibrate(self):
        # 10 second timer, every time max/min changes reset the timer
        end_time = time() + 10

        mag_x, mag_y, mag_z = self.ih.magnetic
        min_x = max_x = mag_x
        min_y = max_y = mag_y
        min_z = max_z = mag_z

        while time() < end_time:
            flag = False
            mag_x, mag_y, mag_z = self.ih.magnetic

            if mag_x < min_x:
                flag = True
                min_x = mag_x
            if mag_y < min_y:
                flag = True
                min_y = mag_y
            if mag_z < min_z:
                flag = True
                min_z = mag_z

            if mag_x > max_x:
                flag = True
                max_x = mag_x
            if mag_y > max_y:
                flag = True
                max_y = mag_y
            if mag_z > max_z:
                flag = True
                max_z = mag_z

            # Hard Iron Correction
            offset_x = (max_x + min_x)/2.0
            offset_y = (max_y + min_y)/2.0
            offset_z = (max_z + min_z)/2.0

            # Soft Iron Correction
            field_x = (max_x - min_x)/2.0
            field_y = (max_y - min_y)/2.0
            field_z = (max_z - min_z)/2.0
            
            if flag: # if any of the max/min values changed wait another 10s
                end_time = time() + 10
            #print("Hard Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(offset_x, offset_y, offset_z))
            #print("Field:    X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(field_x, field_y, field_z))
            #print("")

            sleep(0.01)


        self.is_calibrated = True
        self.is_calibrating = False
        self.log("finished calibrating")
        return 0


#----------------------------run time---------------------------------
    def new_process(self):
        stop_flag = mp.Event()
        process = mp.Process(target=self.run, args=(stop_flag,))
        self.processes.append({"process" : process, "stop flag" : stop_flag, "start time" : time()})
        process.start()
        self.log("process started")
        sleep(0.003)
        if len(self.processes) == 2:
            prevProcessDict = self.processes.pop(0)
            prevProcessDict["stop flag"].set()
        if len(self.processes) > 2:
            self.log("too many processes!!")


    def kill_all(self):
        for t in self.processes:
            t["stop flag"].set()

    def run(self, flag):
        file = open(self.wd + str(floor(time())), "wb+")
        t0 = time()
        while not flag.is_set():
            if time() - t0 > 1/100:
                t = time()
                mx, my, mz = self.ih.magnetic
                bin_data = struct.pack("<dfff", t, mx, my, mz)
                file.write(bin_data)
                t0 = t
        self.log("process finished")


#----------------- not runtime ---------------------------------------
    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                bin_dat = file.read(20)
                data += [struct.unpack("<dfff", bin_dat)] # magx, magy, magz
            except Exception as e:
                self.log("got error reading data, returned processed data")
                self.log(str(e))
                return data
        self.log("process finished running")
        return data
    
    def test(self):
        while True:
            ax = self.ih.magnetic
            print("%12.5f, %12.5f, %12.5f" %(ax[0], ax[1], ax[2]))

if __name__ == '__main__':
    with open("/home/fissellab/BVEXTracker/output/magLog", "a") as log:
        sens = Magnetometer("/home/fissellab/BVEXTracker/output/Magnetometer/", log)
        sens.test()

        quit()







