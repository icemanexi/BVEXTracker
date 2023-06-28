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
	def __init__(self, Write_Directory):
		self.wd = Write_Directory # write directory
		self.threads = []
		self.ih = bno055.BNO055_I2C(I2C(1)) # ih = interface handler
		self.data=[]
		self.header = ["time", "accel x", "accel y", "accel z", "mag x", "mag y", "mag z", "gyro x", "gyro y", "gyro z", "euler 1", "euler 2", "euler 3", "quat 1", "qaut 2", "quat 3", "lin accel x", "lin accel y", "lin accel z", "gravity x", "gravity y", "gravity z"]

		print("IMU initialized")

	def new_thread(self):
		stop_flag = True
		thread = threading.Thread(target=self.run, args=(stop_flag,))
		self.threads.append((thread, stop_flag))
		thread.start()
		sleep(0.001)
		if len(self.threads) == 2:
			prevThread, prevFlag = self.threads.pop(0)
			prevFlag = False
		if len(self.threads) > 2:
			print("Something went wrong with the threading in IMU!")

	def kill_all_threads(self):
		for _, flag in self.threads:
			flag = False


	def run(self, flag):
		t0 = time()
		file = open(self.wd + str(floor(time())), "wb+")
		try:
			while flag: #not flag.is_set():
				#print(time())
				#print("temp   ", self.ih.temperature)
				print(time() - t0, " ", self.ih.acceleration)
				#print("mag:   ", self.ih.magnetic)
				#print("gyro   ", self.ih.gyro)
				#print("euler  ", self.ih.euler)
				#print("quat   ", self.ih.quaternion)
				#print("lina   ", self.ih.linear_acceleration)
				#print("grav   ", self.ih.gravity)
		except Exception as e:
			print("error while running imu: ", e)
			file.close()
		file.close()
		print("finished running imu thread")



	def test(self):
		while True:
			print(self.ih.acceleration)

if __name__ == "__main__":
	test = IMU("/home/fissellab/BVEXTracker-main/output/IMU/")
	test.new_thread()

