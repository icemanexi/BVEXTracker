from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import threading
from math import floor
from numpy import save

try:
	import Sensors.adafruit_bno055 as bno055
except:
	import adafruit_bno055 as bno055

class IMU:
	def __init__(self, Write_Directory):
		self.wd = Write_Directory # write directory
		self.wf = None # write file
		self.thread = None
		self.alive = True
		self.ih = bno055.BNO055_I2C(I2C(1)) # ih = interface handler
		self.data=[]
		self.t0 = -1
		print("IMU initialized")

	def kill(self):
		self.alive = False
		self.thread.join()
		print("IMU ended")

	def begin(self):
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.start()
		self.alive = True
		print("IMU started")

	def save_data(self):
		self.kill()
		self.thread.join()
		assert self.t0 > 0 # make sure data has been collected
		save(self.wd + str(floor(self.t0)), self.data)
		print("IMU data saved, data started at t=", self.t0)

	def run(self):
		self.data = ["time", "ax", "ay", "az", "mx", "my", "mz", "gyx", "gyy", "gyz", "eu1", "eu2", "eu3", "quat1", "qaut2", "quat3", "linax", "linay", "linaz", "gx", "gy", "gz"] # clears data 
		self.t0 = time()
		while self.alive:
			self.data += [time()]
			self.data += list(self.ih.acceleration)
			self.data += list(self.ih.magnetic)
			self.data += list(self.ih.gyro)
			self.data += list(self.ih.euler)
			self.data += list(self.ih.quaternion)
			self.data += list(self.ih.linear_acceleration)
			self.data += list(self.ih.gravity)

	def test(self):
		while True:
			print(self.ih.acceleration)

if __name__ == "__main__":
	test = IMU("/home/fissellab/BVEXTracker-main/output/IMU/")
	test.test()

