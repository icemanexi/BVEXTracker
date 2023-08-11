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

REG_FIFO_DATA = 0x11

class Accelerometer:
    def __init__(self, Write_Directory, log_file, rate=1000):
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
        factor = 2.048 * 2 / 2**20
        try:
            t0 = time()
            t = time()
            
            while not flag.is_set():
                t = time()
                x = self.ih.read(REG_FIFO_DATA, 3)
                length = 0
                res = []
                while(x[2] & 0b10 == 0):
                    x = self.ih.twocomp((x[0] << 12) | (x[1] << 4) | ((x[2] & 0xF0) >> 4))
                    y = self.ih.read(REG_FIFO_DATA, 3)
                    y = self.ih.twocomp((y[0] << 12) | (y[1] << 4) | ((y[2] & 0xF0) >> 4))
                    z = self.ih.read(REG_FIFO_DATA, 3)
                    z = self.ih.twocomp((z[0] << 12) | (z[1] << 4) | ((z[2] & 0xF0) >> 4))
                    res = [[x, y, z]] + res
                    length += 1
                    x = self.ih.read(REG_FIFO_DATA, 3)
                for i in range(length): # the final element is the correctly timestamped read 
                    if i == length - 1:
                        bin_data = struct.pack("<diii", t, res[i][0], res[i][1], res[i][2])
                        file.write(bin_data)
                    else:
                        bin_data = struct.pack("<diii", 0,  res[i][0], res[i][1], res[i][2])
                        file.write(bin_data)
                
                sleep(0.0005)

        except Exception as e:
                self.log(str(e))
                file.close()

        file.close()
        self.log("thread finished")

    def get3Vfifo(self):
        res = []
        times = []
        x = self.read(REG_FIFO_DATA, 3)
        while(x[2] & 0b10 == 0):
            y = self.read(REG_FIFO_DATA, 3)
            z = self.read(REG_FIFO_DATA, 3)
            res.append([x, y, z])
            x = self.read(REG_FIFO_DATA, 3)
            #times.append(time.time())
            
        # convert the data to Gs    
        rawdata = self.convertlisttoRaw(res)
        #gdata = self.convertRawtog(rawdata)
        
        #gdata = self.flatten_list(gdata)
        
        datalist = gdata #times + gdata
        
        return datalist

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
                print(ax)

            #if len(ax) == 4:
                #print("\r\r%8.5f, %8.5f, %8.5f" %(ax[1], ax[2], ax[3]))

if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/Logs/accelLog", "a") as l:
        test = Accelerometer("/home/fissellab/BVEXTracker/output/Accelerometer/", l)

        f = mp.Event()
        test.run(f)
        sleep(10)
        f.set()

        #with open("/home/fissellab/BVEXTracker/output/Accelerometer/1691519550", "rb") as f:
        #    dat = test.read_file(f)
        #    for l in dat:
        #        print(l)
