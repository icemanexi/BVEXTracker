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
		self.name = "Magnetometer"
		self.is_calibrated = False
		print("Magnetometer initialized")

	def calibrate(self):
		cal_thread = threading.Thread(target = self.run_calibrate, args=())
		cal_thread.start()

	def run_calibrate(self):
		# 10 second timer, every time max/min changes reset the timer
		end_time = time() + 10

		mag_x, mag_y, mag_z = self.ih.magnetic
		min_x = max_x = mag_x
		min_y = max_y = mag_y
		min_z = max_z = mag_z

		while time() < end_time:
			flag = False
			mag_x, mag_y, mag_z = self.ih.magnetic

			if mag_x < min_x:
				flag = True
				min_x = mag_x
			if mag_y < min_y:
				flag = True
				min_y = mag_y
			if mag_z < min_z:
				flag = True
				min_z = mag_z

			if mag_x > max_x:
				flag = True
				max_x = mag_x
			if mag_y > max_y:
				flag = True
				max_y = mag_y
			if mag_z > max_z:
				flag = True
				max_z = mag_z

			# Hard Iron Correction
			offset_x = (max_x + min_x)/2.0
			offset_y = (max_y + min_y)/2.0
			offset_z = (max_z + min_z)/2.0

			# Soft Iron Correction
			field_x = (max_x - min_x)/2.0
			field_y = (max_y - min_y)/2.0
			field_z = (max_z - min_z)/2.0
			
			if flag: # if any of the max/min values changed wait another 10s
				end_time = time() + 10
			#print("Hard Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(offset_x, offset_y, offset_z))
			#print("Field:    X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(field_x, field_y, field_z))
			#print("")

			sleep(0.01)


		self.is_calibrated = True
		return 0


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
			ax = self.ih.magnetic
			print("%8.5f, %8.5f, %8.5f" %(ax[0], ax[1], ax[2]))

if __name__ == '__main__':
	sens = Magnetometer("~/BVEXTracker/output/Magnetometer")
	sens.calibrate()







