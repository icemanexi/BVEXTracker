import time
import numpy as np
import spidev
from datetime import datetime

WHOAMI = 0x0F
CTRL1 = 0x20
CTRL2 = 0x21
CTRL3 = 0x22
CTRL4 = 0x23
CTRL5 = 0x24
STATUS = 0x27
LOW_ODR = 0x39
TEMP = 0x26

OUT_X_L = 0x28
OUT_X_H = 0x29
OUT_Y_L = 0x2A
OUT_Y_H = 0x2B
OUT_Z_L = 0x2C
OUT_Z_H = 0x2D

READ_BIT = 0X80
WRITE_BIT = 0X00
DUMMY_BYTE = 0xAA

#SPI settings
SPI_MAX_CLOCK_HZ = 10000000  # Hz
SPI_MODE = 0b01
SPI_BUS = 0
SPI_DEVICE = 1  # change for different chip select

class L3GD20H:
    
    def __init__(self): # SPI enabled
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_MAX_CLOCK_HZ
        self.spi.mode = SPI_MODE
        odr = self.power()

    # read and write register functions using SPI
    def writeRegister(self, address, value): # writes to the gyroscope's addresses
        device_address = WRITE_BIT | address
        self.spi.xfer2([device_address, value])
        
    def readRegister(self, address):# Read registers from the gyroscope
        device_address = READ_BIT | address
        return self.spi.xfer2([device_address, DUMMY_BYTE])[1]
        
    def check_device(self):   # checking if device is detected
        return self.readRegister(WHOAMI)
        
    # power device and change for odr
    def power(self):  
        self.writeRegister(CTRL1, 0xEF)   # change this for ODR, refer to datasheet 
        return self.readRegister(CTRL1)
        
    def reset(self):
        self.writeRegister(LOW_ODR, 0b10)
        rest = self.readRegister(LOW_ODR)
        return rest

    def read_axes(self):
        
        gx = self.readRegister(OUT_X_H) << 8 | self.readRegister(OUT_X_L)  # MSB first
        gy = self.readRegister(OUT_Y_H) << 8 | self.readRegister(OUT_Y_L)
        gz = self.readRegister(OUT_Z_H) << 8 | self.readRegister(OUT_Z_L)

        # make sure axes read out 16 bits
        #gx = np.int16(gx) * 0.00875     # multiply by conversion factor pg 10
        #gy = np.int16(gy) * 0.00875
        #gz = np.int16(gz) * 0.00875
        
        # subtract bias mean to calibrate gyroscope
        #gx = gx + 1.256171414184
        #gy = gy - 1.654750684812
        #gz = gz - 0.489359026685
        
        timestamp = time.time()
        
        gyrodata = list([timestamp, gx, gy, gz])

        return gyrodata

        

        

    


