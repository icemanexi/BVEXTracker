import spidev
from time import time, sleep
import threading
import multiprocessing as mp
from math import floor
import struct
from adafruit_extended_bus import ExtendedI2C as I2C
from struct import unpack_from
import subprocess
import smbus

from Sensors.adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
from Sensors.Log import Log
from Sensors.L3GD20H import L3GD20H
import Sensors.adafruit_bno055 as bno055
from Sensors.adafruit_lis3mdl import LIS3MDL, Rate
from Sensors.gpsModule import ubx, gps_io

# ---------- Accelerometer -----------

spi = spidev.SpiDev()
spi.open(0, 0) # 
spi.max_speed_hz = 10000000
spi.mode = 0b00

rate = 1000
acc_ih = ADXL355(spi.xfer2)
acc_ih.start()
acc_ih.setrange(SET_RANGE_2G) # set range to 2g
acc_ih.setfilter(lpf = ODR_TO_BIT[rate]) # set data rate

# ---------- Gyroscope ----------

gyr_ih = L3GD20H()
gyr_ih.power()


# ---------- IMU ----------

imu_ih = bno055.BNO055_I2C(I2C(1))
imu_ih.mode = 0x0C # NDOF / "normal" mode

# ---------- Magnetometer ----------

mag_ih = LIS3MDL(I2C(1))

# ---------- i2c GPS ----------

i2c_gps_ih = smbus.SMBus(1) # i2c_bus = 1

# ---------- ser GPS ----------

gpsio = gps_io(input_speed=(38400))
ubxt = ubx.ubx()
ubxt.io_handle = gpsio

# ---------- Read functions ----------


def acc_read():
    t = time()
    fifo = acc_ih.get3Vfifo()
    l = len(fifo)
    for i in range(l//3):
        print(fifo[i-l])
    return

    #return time(), acc_ih.getXRaw(), acc_ih.getYRaw(), acc_ih.getZRaw()

def gyr_read():
    return time(), gyr_ih.read_axes()

def imu_read():
    return time(), imu_ih.acceleration, imu_ih.magnetic, imu_ih.gyro, imu_ih.euler

def mag_read():
    return time(), mag_ih.magnetic

# ---------- Main loop ----------



def main_process(flag):
    t = str(floor(time()))

    acc_file = open("/home/fissellab/BVEXTracker/output/Accelerometer/" + t, "wb")
    gyr_file = open("/home/fissellab/BVEXTracker/output/Gyroscope/" + t, "wb")
    mag_file = open("/home/fissellab/BVEXTracker/output/Magnetometer/" + t, "wb")
    imu_file = open("/home/fissellab/BVEXTracker/output/IMU/" + t, "wb")
    i2c_gps_file = open("/home/fissellab/BVEXTracker/output/i2c_GPS/" + t, "wb")
    ser_gps_file = open("/home/fissellab/BVEXTracker/output/ser_GPS/" + t, "wb")

    acc_count = 1 
    gyr_count = 3
    mag_count = 1
    imu_count = 8
    gps_count = 39
    t0 = time()
    gt0 = time()
    mt0 = time()
    it0 = time()


    while not flag.is_set():
        if time() - t0 > 0.00125: # decrement every 1/800th of a second
            t0 = time()
            gyr_count -= 1      
            mag_count -= 1
            imu_count -= 1
            gps_count -= 1

            t = time()
            fifo = acc_ih.get3Vfifo()
            l = len(fifo)
            for i in range(l):
                bin_dat = struct.pack("<diii", t-0.001*i, fifo[i-l][0], fifo[i-l][1], fifo[i-l][2])
                acc_file.write(bin_dat)
            

        if not gyr_count:
            print("gyr: ", 1/(time() - gt0))
            gt0 = time()
            t, l = gyr_read()
            bin_dat = struct.pack("<dHHH", t, l[0], l[1], l[2])
            gyr_file.write(bin_dat)
            gyr_count = 4

        if not mag_count:
            print("mag: ", 1/(time() - mt0))
            mt0 = time()
            t, l = mag_read()
            bin_dat = struct.pack("<dfff", t, l[0], l[1], l[2])
            mag_file.write(bin_dat)
            mag_count = 4

        if not imu_count:
            print("imu: ", 1/(time() - it0))
            it0 = time()
            t, a,g,m,e = imu_read()
            bin_dat = struct.pack("<dffffffffffff", t,a[0],a[1],a[2],g[0],g[1],g[2],m[0],m[1],m[2],e[0],e[1],e[2])
            imu_file.write(bin_dat)
            imu_count = 8

        if not gps_count:
            pass



if __name__ == "__main__":
    flag = mp.Event()
    p = mp.Process(target=main_process, args=(flag,))
    p.start()
    sleep(60)
    flag.set()



    # main process management 
