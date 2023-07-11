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
        self.is_calibrating = False

        
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
            return
        self.is_calibrating = True
        status_reg =  self.ih._read_register(0x35)
        sys_stat = (status_reg & 0b11000000) >>6
        gyr_stat = (status_reg & 0b00110000) >> 4
        acc_stat = (status_reg & 0b00001100) >> 2
        mag_stat = (status_reg & 0b00000011)
        #print("\n IMU cali status: sys: ", sys_stat, "gy", gyr_stat, "ac", acc_stat, "ma", mag_stat)
        

        if (status_reg & 0b00110011) == 0b00110011:
            self.is_calibrating = False
            return True
        return False


    def new_thread(self):
        stop_flag = threading.Event()
        thread = threading.Thread(target=self.run, args=(stop_flag,))
        self.threads.append({"thread" : thread, "stop flag" : stop_flag, "start time" : time()})
        thread.start()
        sleep(0.003)
        self.log.write("\nIMU: thread started")
        print("IMU: thread started")
        if len(self.threads) == 2:
            prevThreadDict = self.threads.pop(0)
            prevThreadDict["stop flag"].set()
        if len(self.threads) > 2:
            self.log.write("\nIMU: too many IMU threads, did not start a new one")

    def kill_all_threads(self):
        for t in self.threads:
            t["stop flag"].set()


    def run(self, flag):
        if not self.ih:
            self.log.write("\nIMU: CRITICAL ERRROR!! intereface handler not defined. ending thread")
            return

        t0 = time()
        t= time()
        dat_file = open(self.wd + str(floor(time())), "wb")
        try:
            while not flag.is_set():
                print(time() - t)
                t = time()
                
                bin_data = struct.pack("<d", t)
                
                x, y, z = self.ih.acceleration
                if None in (x ,y, z):
                    x = y = z = -999
                bin_data += struct.pack("<fff", x,y,z)
                
                x, y, z = self.ih.magnetic
                if None in (x ,y, z):
                    x = y = z = -999
                bin_data += struct.pack("<fff", x, y, z)
                
                x, y, z = self.ih.gyro
                if None in (x ,y, z):
                    x = y = z = -999
                bin_data += struct.pack("<fff", x, y, z)
                
                x, y, z = self.ih.euler
                if None in (x ,y, z):
                    x = y = z = -999
                bin_data += struct.pack("<fff", x, y, z)
                
                dat_file.write(bin_data)
        except Exception as e:
            self.log.write("\nIMU:" + str(e))
            dat_file.close()
        dat_file.close()
        self.log.write("\nIMU: finished running thread")

# ------------------------not runtime--------------------------
    # saving raw data from sensor, these convert numbers to default units
    # see data sheet
    scales = {
            "acceleration" : 0.01,
            "magnetic" : 0.0625,
            "gyro" : 0.001090830782496456,
            "euler" : 0.0625,
            "quaternion" : (1 / (1<<14)),
            "linear accel" : 0.01,
            "gravity" : 0.01
            }

    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                bin_dat = file.read(8)
                data += [struct.unpack("<d", bin_dat)[0]]
                bin_dat = file.read(12)
                data += [i*scales["acceleration"] for i in struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [i*scales["magnetic"] for i in struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [i*scales["gyro"] for i in struct.unpack("<fff", bin_dat)]
                bin_dat = file.read(12)
                data += [i*scales["euler"] for i in struct.unpack("<fff", bin_dat)]
            except Exception as e:
                print(e)
                print("IMU: got error reading data, returned processed data")
                return data
        return data

    def test(self):
        if not self.ih:
            print("IMU: ih not defined, exiting")
            return
        from math import sqrt
        while True:
            #print(self.ih.calibration_status)
            #ax = self.ih.gyro
            #print(hex(self.ih._read_register(0x00)))
            
            #print("-"*30)
            #print("\r\rGyro: %8.5f, %8.5f, %8.5f" %(ax[0], ax[1], ax[2]))
            
            ax = self.ih.acceleration
            if None not in ax:
                print("\r\rAcc:  %20f, %20f, %20f" %(ax[0], ax[1], ax[2]))
            else:
                print(ax)
            sleep(0.005)


if __name__ == "__main__":
    with open("/home/fissellab/BVEXTracker/output/IMULog", "a") as log:
        test = IMU("/home/fissellab/BVEXTracker/output/IMU/", log)
        #test.new_thread()
    #while not test.is_calibrated:
    #    sleep(1)
    test.test()

