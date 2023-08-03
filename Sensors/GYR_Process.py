from time import sleep, time
from numpy import save
from math import floor
import struct
import threading
import spidev

try:
    from Sensors.L3GD20H import L3GD20H
    from Sensors.adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Sensors.Log import Log
except:
    from L3GD20H import L3GD20H
    from adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
    from Log import Log


gyr_ih = L3GD20H()
gyr_ih.power()

acc_spi = spidev.SpiDev()
acc_spi.open(0, 0) # bus=0, cs=0
acc_spi.max_speed_hz = 10000000
acc_spi.mode = 0b00

ACC_RATE = 4000
acc_ih = ADXL355(acc_spi.xfer2)
acc_ih.start()
acc_ih.setrange(SET_RANGE_2G) # set range to 2g
acc_ih.setfilter(lpf = ODR_TO_BIT[ACC_RATE]) # set data rate


gt0 = time()
while True:
    dat = gyr_ih.read_axes()
    print("gy", 1/(time()-gt0), dat)
    gt0 = time()
    sleep(0.0010)

