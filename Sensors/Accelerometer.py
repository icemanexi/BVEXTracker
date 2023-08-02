import spidev
from time import time, sleep
import threading
from math import floor
import struct

try:
    from adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Log import Log
except:
    from Sensors.adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Sensors.Log import Log

class Accelerometer:
    def __init__(self, Write_Directory, log_file, rate=1000):
        self.wd = Write_Directory
        self.log = Log("ACC:", log_file)
        self.threads = []
        self.rate = rate # valid: 4000, 2000, 1000, 500, 250, 125
        self.key = "<dfff"
        self.header = ["time", "accel x", "accel y", "accel z"]
        self.name = "Acceleromter"
        self.is_calibrated = True # does not require calibration
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

    def new_thread(self):
        stop_flag = threading.Event()
        thread = threading.Thread(target=self.run, args=(stop_flag,))
        self.threads.append({"thread" : thread, "stop flag" : stop_flag, "start time" : time()})
        thread.start()
        sleep(0.003)
        self.log("thread started")

        if len(self.threads) == 2:
            prevThreadDict = self.threads.pop(0)
            prevThreadDict['stop flag'].set()
        if len(self.threads) > 2:
            self.log("too many accelerometer threads!")

    def kill_all_threads(self):
        for t in self.threads:
            t['stop flag'].set()

    def run(self, flag):
        file = open(self.wd + str(floor(time())), "wb+")

        try:
            while not flag.is_set():
                data = self.ih.get3Vfifo()
                if len(data) == 4: #make sure data is not empty
                    bin_data = struct.pack("<dfff", data[0], data[1], data[2], data[3])
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
                data += [struct.unpack("<dfff", bin_dat)]
            except Exception as e:
                print(e)
                print("got error reading data, returned processed data")
                return data
        return data


    def test(self):
        num = 0
        while True:
            t0 = time()
            num +=1
            ax = self.ih.get3Vfifo()
            if time() - t0 > 0.001:
                print(num)
                print("yes")
                print(time() - t0)


            #if len(ax) == 4:
                #print("\r\r%8.5f, %8.5f, %8.5f" %(ax[1], ax[2], ax[3]))

if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/output/accelLog", "a") as l:
        test = Accelerometer("/home/fissellab/BVEXTracker/output/Accelerometer/", l)
        test.test()
        #test.new_thread()
        #sleep(60)
        #test.kill_all_threads()
        #with open("/home/fissellab/BVEXTracker/output/Accelerometer/1690831806", "rb") as f:
        #    dat = test.read_file(f)
        #    for ax in dat:
        #        print("\r\r%8.5f, %8.5f, %8.5f" %(ax[1], ax[2], ax[3]))




