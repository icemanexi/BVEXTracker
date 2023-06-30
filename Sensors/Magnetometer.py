from time import sleep, time
from adafruit_extended_bus import ExtendedI2C as I2C
import threading
from math import floor
import struct

try:
	from adafruit_lis3mdl import LIS3MDL, Rate
except:
	from Sensors.adafruit_lis3mdl import LIS3MDL, Rate

class Magnetometer:
	def __init__(self, Write_Directory):
		self.wd =Write_Directory
		self.threads = []
		self.ih = LIS3MDL(I2C(1))
        self.header = ("time", "mag x", "mag y", "mag z")
		print("Magnetometer initialized")


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
		file = open(self.wd + str(floor(time())), "wb+")
        while flag.is_set():
            bin_data = struct.pack("<d", time())
			mx, my, mz = self.ih.magnetic
            bin_data += struct.pack("<fff", mx, my, mz)
            file.write(bin_data)

	def read_file(self, file):
		data = [self.header]
		while True:
			try:
				bin_dat = file.read(8)
				data += [struct.unpack("<d", bin_dat)[0]] # time

				bin_dat = file.read(12)
				data += [struct.unpack("<fff", bin_dat)] # magx, magy, magz
			except Exception as e:
				print(e)
				print("got error reading data, returned processed data")
				return data
		return data
	
    def test(self):
		while True:
			print([time(), self.ih.magnetic])

if __name__ == '__main__':
	sens = Magnetometer("~/BVEXTracker/output/Magnetometer")
	sens.test()






