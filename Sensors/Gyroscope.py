from time import sleep, time
from numpy import save
from math import floor
import struct
import multiprocessing as mp

try:
    from Sensors.L3GD20H import L3GD20H
    from Sensors.Log import Log
except:
    from L3GD20H import L3GD20H
    from Log import Log



class Gyro:
    def __init__(self, Write_Directory : str, log_file): #runs upon initialization
        self.wd = Write_Directory
        self.log = Log("GYR:", log_file)
        self.header = ("time", "gyro x", "gyro y", "gyro z")
        self.key = "<dHHH" # this is used for the struct methods
        self.processes = []
        self.name = "Gyroscope"
        self.is_calibrating = False
        self.is_calibrated = True # gyro does not need to be calibrated
        
        try:
            # TODO write script to ensure connection 
            # eg read whoami reg
            self.ih = L3GD20H()
            self.ih.power()
            self.log("initialized")
        except Exception as e:
            self.ih = None
            self.log("CRITICAL ERROR!! could not initialize interface handler:" + str(e))
            raise e

    def new_process(self):
        stop_flag = mp.Event()
        process = mp.Process(target=self.run, args=(stop_flag,))
        self.processes.append({"thread" : process, "stop flag" : stop_flag, "start time" : time()})
        process.start()
        sleep(0.003)
        self.log("started new thread")
        if len(self.processes) == 2:
            prevProcessDict = self.processes.pop(0)
            prevProcessDict["stop flag"].set()
        if len(self.processes) > 2:
            self.log("too many gyro threads, did not start a new one")


    def kill_all(self):
        for t in self.processes:
            t["stop flag"].set()

    def run(self, flag):
        if not self.ih:
            self.log("CRITICAL ERROR!! interface handler not defined. ending thread")
            return

        file = open(self.wd + str(floor(time())), "wb")
        try:
            prev = time()
            while not flag.is_set():
                if self.ih.readRegister(0x27) & 0b00001000 == 0b00001000: # new data check
                    axes = self.ih.read_axes()
                    bin_data = struct.pack("<dHHH", time(),  axes[0], axes[1], axes[2])
                    file.write(bin_data)
        except Exception as e:
            self.log("error whle collecting data:", str(e))
            file.close()

        file.close()

        self.log("finished running thread")


# ------------------------not runtime--------------------------
    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                bin_dat = file.read(20)
                print(bin_dat)
                if not bin_dat:
                    break
                data += [struct.unpack("<dfff", bin_dat)]
            except Exception as e:
                print(e)
                print("GYRO: got error reading data, returned processed data")
                return data
        return data

    def test(self):
        while True:
            stat = self.ih.readRegister(0x27)
            #print(stat)
            prev = time()
            if stat & 0b00001000 == 0b00001000:
                t, x, y ,z = self.ih.read_axes() 
                #print(1 /(t-prev))
                prev=t
                #print("%8.2f, %8.2f, %8.2f" %(x, y, z))



if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/Logs/gyroLog", "a") as f:
        test = Gyro("/home/fissellab/BVEXTracker/output/Gyroscope/", f)
        test.new_process()

