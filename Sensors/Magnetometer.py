from time import sleep, time
from numpy import save
from adafruit_extended_bus import ExtendedI2C as I2C
import threading
from math import floor

try:
	from adafruit_lis3mdl import LIS3MDL, Rate
except:
	from Sensors.adafruit_lis3mdl import LIS3MDL, Rate

class Magnetometer:
	def __init__(self, Write_Directory):
		self.wd =Write_Directory
		self.thread = None
		self.alive = True
		self.ih = LIS3MDL(I2C(1))
		self.data = []
		self.t0 = -1
		print("Magnetometer initialized")

	def kill(self):
		self.alive = False
		self.thread.join()
		print("Magnetometer ended")
		
	def begin(self):
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.start()
		self.alive = True
		print("Magnetometer started")
	
	def save_data(self):
		self.kill()
		self.thread.join()
		
		assert self.t0 > 0 # make sure data has been collected
           # filename 				item to save
		save(self.wd + str(floor(self.t0)), self.data)

		print("IMU data saved, data started at t=", self.t0)

	def run(self):
		self.data = ["time", "magx","magy", "magz", "temp"]
		self.t0 = time()
		while self.alive:
			self.data += [time()]
			self.data += list(self.ih.magnetic)
			self.data += [self.ih.get_temp]

	def test(self):
		while True:
			print([time(), self.ih.magnetic])

if __name__ == '__main__':
	sens = Magnetometer("~/BVEXTracker/output/Magnetometer")
	sens.test()






