#!/usr/bin/env python3
from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import threading
from math import floor
from numpy import save
import struct

try:
	import Sensors.adafruit_bno055 as bno055
except:
	import adafruit_bno055 as bno055

imu = bno055.BNO055_I2C(I2C(1))


arr = [1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9]
t0 = time()
filename = str(floor(t0)) + ".bin"
print(filename)
with open(filename, "wb") as file:
	for e in arr:
		p = struct.pack('f', e)
		print(e)
		file.write(p)
print("-----------")
with open(filename, "rb") as file:
	data = []
	while True:
		binary_data = file.read(4)
		if not binary_data:
			break
		val = struct.unpack('f', binary_data)[0]
		data.append(val)
		print(val)


