import spidev
from time import time, sleep
import threading
import multiprocessing as mp
from math import floor
import struct

try:
    from adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Log import Log
except:
    from Sensors.adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Sensors.Log import Log

class Accelerometer:
    def __init__(self, Write_Directory, log_file, rate=4000):
        self.wd = Write_Directory
        self.log = Log("ACC:", log_file)
        self.processes = []
        self.rate = rate # valid: 4000, 2000, 1000, 500, 250, 125
        self.key = "<dfff"
        self.header = ["time", "accel x", "accel y", "accel z"]
        self.name = "Acceleromter"
        self.is_calibrating = False

        # SETUP SPI AND ACCELEROMTER
        try:
            spi = spidev.SpiDev()
            spi.open(0, 0) # bus=0, cs=0
            spi.max_speed_hz = 10000000
            spi.mode = 0b00
            self.ih = ADXL355(spi.xfer2)
            self.ih.start()
            self.ih.setrange(SET_RANGE_2G) # set range to 2g
            self.ih.setfilter(lpf = ODR_TO_BIT[rate]) # set data rate
            
            # TODO: ensure conntection to accelerometer in init by checking whoami reg
            # otherwise, raise error
            #self.interface_handler.dumpinfo()
            
        except Exception as e:
            raise e
        else:
            self.log("initialized")

    @property
    def is_calibrated(self):
        if self.ih.whoami() == 237:
            return True
        return False

    def new_process(self):
        stop_flag = mp.Event()
        process = mp.Process(target=self.run, args=(stop_flag,))
        self.processes.append({"thread" : process, "stop flag" : stop_flag, "start time" : time()})
        process.start()
        sleep(0.003)
        self.log("thread started")

        if len(self.processes) == 2:
            prevProcessDict = self.processes.pop(0)
            prevProcessDict['stop flag'].set()
        if len(self.processes) > 2:
            self.log("too many accelerometer threads!")

    def kill_all(self):
        for t in self.processes:
            t['stop flag'].set()

    def run(self, flag):
        file = open(self.wd + str(floor(time())), "wb+")

        try:
            while not flag.is_set():
                if time() - t > 0.00125:
                    t = time()
                    x, y, z = self.ih.getXRaw(), self.ih.getYRaw(), self.ih.getZRaw()
                    bin_data = struct.pack("<diii", t, x, y, z)
                    file.write(bin_data)

        except Exception as e:
                self.log(str(e))
                file.close()

        file.close()
        self.log("thread finished")


#-------------------------not runtime-----------------------------
    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                bin_dat = file.read(20)
                if not bin_dat:
                    break
                data += [struct.unpack("<diii", bin_dat)]
            except Exception as e:
                print(e)
                print("got error reading data, returned processed data")
                return data
        return data


    def test(self):
        num = 0
        while True:
            t0 = time()
            ax = self.ih.get3Vfifo()
            if time() - t0 > 0.001:
                print("yes")
                print(time() - t0)


            #if len(ax) == 4:
                #print("\r\r%8.5f, %8.5f, %8.5f" %(ax[1], ax[2], ax[3]))

if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/Logs/accelLog", "a") as l:
        test = Accelerometer("/home/fissellab/BVEXTracker/output/Accelerometer/", l)
        with open("/home/fissellab/BVEXTracker/output/Accelerometer/1691160582", "rb") as f:
            print(test.read_file(f))

