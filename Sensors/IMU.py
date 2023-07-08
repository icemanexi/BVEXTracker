from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import threading
from math import floor
import struct


try:
    import Sensors.adafruit_bno055 as bno055
except:
    import adafruit_bno055 as bno055

class IMU:
    def __init__(self, Write_Directory, log):
        self.wd = Write_Directory # write directory
        self.name = "IMU"
        self.threads = []
        self.log = log
        self.header = ("time", "accel x", "accel y", "accel z", "mag x", "mag y", "mag z", "gyro x", "gyro y", "gyro z", "euler 1", "euler 2", "euler 3")
        
        try:
            # will throw error if not connected
            self.ih = bno055.BNO055_I2C(I2C(1)) # ih = interface handler
        except Exception as e:
            self.ih = None
            raise e
        else:
            self.log.write("\nIMU: initialized")



    @property
    def is_calibrated(self):
        if not self.ih:
            self.log.write("\nIMU: CRITICAL ERROR!! interface handler not defined, cant calibrate")
            return False
        status_reg =  self.ih._read_register(0x35)
        sys_stat = (status_reg & 0b11000000) >>6
        gyr_stat = (status_reg & 0b00110000) >> 4
        acc_stat = (status_reg & 0b00001100) >> 2
        mag_stat = (status_reg & 0b00000011)
        print("\n IMU cali status: sys: ", sys_stat, "gy", gyr_stat, "ac", acc_stat, "ma", mag_stat)
        return (status_reg & 0b00110011) == 0b00110011


    def new_thread(self):
        stop_flag = threading.Event()
        thread = threading.Thread(target=self.run, args=(stop_flag,))
        self.threads.append((thread, stop_flag))
        thread.start()
        sleep(0.003)
        if len(self.threads) == 2:
            prevThread, prevFlag = self.threads.pop(0)
            prevFlag.set()
        if len(self.threads) > 2:
            self.log.write("\nIMU: too many IMU threads, did not start a new one")

    def kill_all_threads(self):
        for _, flag in self.threads:
            flag.set()


    def run(self, flag):
        if not self.ih:
            self.log.write("\nIMU: CRITICAL ERRROR!! intereface handler not defined. ending thread")
            return

        t0 = time()
        t= time()
        dat_file = open(self.wd + str(floor(time())), "wb+")
        try:
            while not flag.is_set():
                prevtime = t
                t = time()
                print(t - prevtime)
                bin_data = struct.pack("<d", time())
                x, y, z = self.ih.acceleration
                bin_data += struct.pack("<fff", x,y,z)
                x, y, z = self.ih.magnetic
                bin_data += struct.pack("<fff", x, y, z)
                x, y, z = self.ih.gyro
                bin_data += struct.pack("<fff", x, y, z)
                x, y, z = self.ih.euler
                bin_data += struct.pack("<fff", x, y, z)
                dat_file.write(bin_data)
        except Exception as e:
            self.log.write("\nIMU:" + str(e))
            dat_file.close()
        dat_file.close()
        self.log.write("\nIMU: finished running thread")

# ------------------------not runtime--------------------------
    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                bin_dat = file.read(8)
                data += [struct.unpack("<d", bin_dat)[0]]
                bin_dat = file.read(12)
                data += [struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [struct.unpack("<fff", bin_dat)]
            except Exception as e:
                print(e)
                print("IMU: got error reading data, returned processed data")
                return data
        return data

    def test(self):
        if not self.ih:
            print("IMU: ih not defined, exiting")
            return
        
        while True:
            #print(self.ih.calibration_status)
            ax = self.ih.gyro
            print(hex(self.ih._read_register(0x00)))
            print("\r\r%8.5f, %8.5f, %8.5f" %(ax[0], ax[1], ax[2]))
            sleep(1)
if __name__ == "__main__":
    with open("/home/bvextp1/BVEXTracker/output/IMULog", "a") as log:
        test = IMU("/home/fissellab/BVEXTracker-main/output/IMU/", log)
    #while not test.is_calibrated:
    #    sleep(1)
    test.test()
