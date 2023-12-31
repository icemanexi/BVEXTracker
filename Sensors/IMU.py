from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import multiprocessing as mp
from math import floor
import struct

try:
    import Sensors.adafruit_bno055 as bno055
    from Sensors.Log import Log
except:
    import adafruit_bno055 as bno055
    from Log import Log

class IMU:
    def __init__(self, Write_Directory, log_file):
        self.wd = Write_Directory # write directory
        self.name = "IMU"
        self.processes = []
        self.log = Log("IMU:", log_file)
        self.header = ("time", "accel x", "accel y", "accel z", "mag x", "mag y", "mag z", "gyro x", "gyro y", "gyro z", "euler 1", "euler 2", "euler 3")
        self.is_calibrating = False
        self.is_calibrated = False

        try:
            # will throw error if not connected
            self.ih = bno055.BNO055_I2C(I2C(1)) # ih = interface handler
        except Exception as e:
            self.ih = None
            raise e
        else:
            self.log("initialized")

    # reads in calibration offsets from file
    def calibrate(self):
        with open("/home/fissellab/BVEXTracker/Sensors/IMU_offsets", "r") as f:
            self.offset_list = [int(i) for i in f.read().split()]

        # these 5 lines load in the preset offset values
        self.ih.mode = 0x00 # 'CONFIG' mode needed to edit offsets
        addr = 0x55 # start of offset registers
        for e in self.offset_list:
            self.ih._write_register(addr, e) # writes in stored offset
            addr += 1
       
        """
        the IMU gets 128 added to values when reading, 
        but I don't think there are any issues with writing
        values to the IMU. so no need for a sanity check.
        """
        # sanity check
        #print("Software offsets:")
        #print(self.offset_list)
        #print("Hardware offsets (x3)")
        #for a in range (3):
        #    addr = 0x55
        #    for i in self.offset_list:
        #        stored = self.ih._read_register(addr)
        #        print(stored, end=", ")
        #        addr += 1
        #    print("")
        

        self.ih.mode = 0x0C # 'NDOF' or 'normal' mode
        self.is_calibrated = True
        self.log("successful calibration")

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
            self.log("too many IMU processes, did not start a new one")

    def kill_all(self):
        for t in self.processes:
            t["stop flag"].set()


    def run(self, flag):
        if not self.ih:
            self.log("CRITICAL ERRROR!! intereface handler not defined. ending process")
            return

        dat_file = open(self.wd + str(floor(time())), "wb")
        try:
            t0 = time()
            while not flag.is_set():
                if time() - t0 > 1/200: 
                    t0 = time()
                    bin_data = struct.pack("<d", time())
                    
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
            self.log(str(e))
            dat_file.close()
        dat_file.close()
        self.log("process finished")

    def get_calibration_offsets(self):
        while True:
            status_reg =  self.ih._read_register(0x35)
            sys_stat = (status_reg & 0b11000000) >>6
            gyr_stat = (status_reg & 0b00110000) >> 4
            acc_stat = (status_reg & 0b00001100) >> 2
            mag_stat = (status_reg & 0b00000011)
            print("\n IMU cali status: sys: ", sys_stat, "gy", gyr_stat, "ac", acc_stat, "ma", mag_stat)
            sleep(1)
            if status_reg & 0b00111111 == 0b00111111: # full calibration
                break
        
        self.ih.mode = 0x00 # 'CONFIG' mode
        start_i = 0x55 # start of calibration registers
        cali_list = []
        for i in range(22):
            cali_list.append(self.ih._read_register(start_i + i))

        print(cali_list)
        with open("/home/fissellab/BVEXTracker/Sensors/IMU_offsets", "w") as f:
            for i in range(len(cali_list)): # write calibration offsets to file
                if i == 21:
                    f.write(str(cali_list[i]))
                    continue
                f.write(str(cali_list[i]) + " ")
            

        self.ih.mode = 0x0C # NDOF mode / normal mode   
        


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
            "gravity" : 0.01,
            "temperature" : 0.5
            }

    def read_file(self, file):
        data = [self.header]
        while True:
            try:
                temp  = []
                bin_dat = file.read(8)
                temp += struct.unpack("<d", bin_dat)
                
                bin_dat = file.read(12)
                temp += struct.unpack("<fff", bin_dat)#[i*scales["acceleration"] for i in struct.unpack("<fff", bin_dat)]
                
                bin_dat = file.read(12)
                temp +=struct.unpack("<fff", bin_dat)#[i*scales["magnetic"] for i in struct.unpack("<fff", bin_dat)]
                
                bin_dat = file.read(12)
                temp += struct.unpack("<fff", bin_dat)#[i*scales["gyro"] for i in struct.unpack("<fff", bin_dat)]
                
                bin_dat = file.read(12)
                temp += struct.unpack("<fff", bin_dat) #[i*scales["euler"] for i in struct.unpack("<fff", bin_dat)]

                data += [temp]
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
        test.test()

