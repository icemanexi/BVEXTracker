from time import sleep, time
from numpy import save
from math import floor
import struct

try:
	from Sensors.L3GD20H import L3GD20H
except:
	from L3GD20H import L3GD20H

import threading


class Gyro:
	def __init__(self, Write_Directory : str): #runs upon initialization
		self.wd = Write_Directory
		self.ih = L3GD20H()
		self.header = ("time", "gyro x", "gyro y", "gyro z")
		self.key = "<dIII" # this is used for the struct methods
		self.threads = [] 
		self.num_threads = 0

		print("gyro initialized")

	def new_thread(self):
		stop_flag = threading.Event()
		thread = threading.Thread(target=self.run, args=(stop_flag,))
		self.threads.append((thread, stop_flag))
		thread.start()
		sleep(0.0005)
		if self.num_threads != 0:
			self.threads[self.num_threads - 1][1].set()
		self.num_threads += 1

	def kill_all_threads(self):
		for _, flag in self.threads:
			flag.set()

	def run(self, flag):
		file = open(self.wd + str(floor(time())), "wb+")
		t0 = time()
		try:
			while not flag.is_set():
				axes = self.ih.read_axes()
				print(t0, axes)
				bin_data = struct.pack("<dIII",  axes[0], axes[1], axes[2], axes[3])
				file.write(bin_data)
				sleep(0.001)
		except Exception as e:
			print("error while running gyro: ", e)
			file.close()

		file.close()

		print("finished running gyro thread")





	def read_file(self, file):
		data = [self.header]

		while True:
			try:
				bin_dat = file.read(20)
				if not bin_dat:
					break
				data += [struct.unpack("<dIII", bin_dat)]
			except:
				print("got error reading data, printing result:\n")
				return data
		return data

	def test(self):
		while True:
			t, x, y ,z = self.ih.read_axes()
			print("%8.2f, %8.2f, %8.2f" %(x, y, z))
			sleep(0.001)


if __name__ == "__main__":
	test = Gyro("/home/fissellab/BVEXTracker-main/output/Gyroscope/")

	test.new_thread()
	sleep(1.5)
	test.new_thread()
	sleep(0.2)
	test.kill_all_threads()



