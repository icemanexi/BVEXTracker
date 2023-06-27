import spidev
from numpy import save
from datetime import datetime
import csv
from time import time, sleep
import threading
from math import floor

try:
	from adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT
except:
	from Sensors.adxl355 import ADXL355, SET_RANGE_2G, ODR_TO_BIT


# function to get rid of nested lists        
def flatten_list(_list):
	flat_list = []
	for element in _list:
		if hasattr(element, '__iter__'): # if the item is iterable
			for item in element:
				flat_list.append(item)
		else:
			flat_list.append(element)
	return flat_list

class Accelerometer:
	def __init__(self, Write_Directory, rate=1000):
		self.wd = Write_Directory
		self.thread = None
		self.alive = True
		self.data= []
		self.t0 = -1
		self.rate = rate # valid: 4000, 2000, 1000, 500, 250, 125

		# SETUP SPI AND ACCELEROMTERE
		spi = spidev.SpiDev()
		spi.open(0, 0) # bus=0, cs=0
		spi.max_speed_hz = 10000000
		spi.mode = 0b00
		self.ih = ADXL355(spi.xfer2)
		self.ih.start()
		self.ih.setrange(SET_RANGE_2G) # set range to 2g
		self.ih.setfilter(lpf = ODR_TO_BIT[rate]) # set data rate
		#self.interface_handler.dumpinfo()
		print("acc initialized")

	def kill(self):
		self.alive=False
		self.thread.join()
		print("acc ended")

	def begin(self):
		self.thread  = threading.Thread(target=self.run, args=())
		self.thread.start()
		self.alive = True
		print("acc started")

	def save_data(self):
		self.kill()
		self.thread.join()
		assert self.t0 > 0 # make sure data has been collected
		save(self.wd + str(floor(self.t0)), self.data)
		print("acc data saved, data started at t=", self.t0)

	def run(self):
		self.data = ["time", "ax", "ay", "az"]
		self.t0 = time()
		try:
			while self.alive:
				self.data += self.ih.get3Vfifo()
		except (OverflowError):
			print("too much data, overflow error")
			self.kill()

	def test(self):
		while True:
			print(self.ih.get3Vfifo())

if __name__ == "__main__":
	test = Accelerometer("/home/fissellab/BVEXTracker-main/output/Accelerometer/")
	test.test()
	sleep(60)
	test.save()
	test.kill()
	

