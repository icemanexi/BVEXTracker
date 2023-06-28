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
		self.header = ("time", "accel x", "accel y", "accel z", "mag x", "mag y", "mag z", "gyro x", "gyro y", "gyro z", "euler 1", "euler 2", "euler 3")

		print("IMU initialized")

	def new_thread(self):
		stop_flag = threading.Event()
		thread = threading.Thread(target=self.run, args=(stop_flag,))
		self.threads.append((thread, stop_flag))
		thread.start()
		sleep(0.001)
		if len(self.threads) == 2:
			prevThread, prevFlag = self.threads.pop(0)
			prevFlag.set()
		if len(self.threads) > 2:
			print("too many IMU threads!!")

	def kill_all_threads(self):
		for _, flag in self.threads:
			flag.set()


	def run(self, flag):
		t0 = time()
		t= time()
		file = open(self.wd + str(floor(time())), "wb+")
		try:
			while not flag.is_set():
				prevtime = t
				t = time()
				print(t - prevtime)
				bin_data = struct.pack("<d", time())
				x, y, z = self.ih.acceleration
				bin_data += struct.pack("<fff", x,y,z)
				x, y, z = self.ih.magnetic
				bin_data += struct.pack("<fff", x, y, z)
				x, y, z = self.ih.gyro
				bin_data += struct.pack("<fff", x, y, z)
				x, y, z = self.ih.euler
				bin_data += struct.pack("<fff", x, y, z)
				file.write(bin_data)
		except Exception as e:
			print("error while running imu: ", e)
			file.close()
		file.close()
		print("finished running imu thread")


	def read_file(self, file):
		data = [self.header]
		while True:
			try:
				bin_dat = file.read(8)
				data += [struct.unpack("<d", bin_dat)[0]]
				bin_dat = file.read(12)
				data += [struct.unpack("<fff", bin_dat)]
				bin_dat = file.read(12)
				data += [struct.unpack("<fff", bin_dat)]
				bin_dat = file.read(12)
				data += [struct.unpack("<fff", bin_dat)]
				bin_dat = file.read(12)
				data += [struct.unpack("<fff", bin_dat)]
			except Exception as e:
				print(e)
				print("got error reading data, returned processed data")
				return data
		return data

	def test(self):
		while True:
			print(self.ih.acceleration)

if __name__ == "__main__":
	test = IMU("/home/fissellab/BVEXTracker-main/output/IMU/")
	with open("/home/fissellab/BVEXTracker-main/output/IMU/1687986790", "rb") as file:
		print(test.read_file(file))

