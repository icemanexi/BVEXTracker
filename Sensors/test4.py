from time import sleep, time
import threading
import spidev
from adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT

spi = spidev.SpiDev()
spi.open(0, 0) # bus=0, cs=0
spi.max_speed_hz = 10000000
spi.mode = 0b00
ih = ADXL355(spi.xfer2)

print(hex(ih.read(0x00)))
print(spi.xfer2([0x01, 0x00]))


