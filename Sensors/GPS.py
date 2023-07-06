#!/usr/bin/python3
from time import time, sleep
from numpy import save
from math import floor
import threading
from struct import unpack_from
try:
	from Sensors.gpsModule import ubx, gps_io
except:
	from gpsModule import ubx, gps_io



class Gps:


	def __init__(self, Write_Directory): #runs upon initialization
		self.wd = Write_Directory
		self.threads = []
		self.gpsio = gps_io(input_speed=38400)
		self.ih = ubx.ubx()
		self.ih.io_handle = self.gpsio
		self.name = "GPS"
		self.is_calibrated = False


		print("gps initialized")

	def calibrate(self):
		cal_thread = threading.Thread(target=self.run_calibrate, args=())
		cal_thread.start()


	fix_types = {
		0 : "no fix",
		1 : "dead reckoning",
		2 : "2d fix",
		3 : "3d fix",
		4 : "GNSS + dead reckoning",
		5 : "time only"
	}

	def run_calibrate(self):
		
		# 3 steps:
		# 0. ensure binary protocol

		# 1. Wait for fix
		no_fix = True
		fix_type = None
		while no_fix:
			out = self.read()

			# TODO: add timeout if no pvt message for too long


			# check if first 4 bytes in message match header of UBX-NAV-PVT
			if b'\xb5b\x01\x07' in out[0:4]:
				nums = unpack_from('<LHBBBBBBLlBBBBllllLLlllllLLHHHH', out[6:], 0)
				#											 trim header ^^

				# for debugging, shows what each number corresponds to
				#s = ('  iTOW %u time %u/%u/%u %02u:%02u:%02u valid x%x\n'
				#	 '  tAcc %u nano %d fixType %u flags x%x flags2 x%x\n'
				#	 '  numSV %u lon %d lat %d height %d\n'
				#	 '  hMSL %d hAcc %u vAcc %u\n'
				#	 '  velN %d velE %d velD %d gSpeed %d headMot %d\n'
				#	 '  sAcc %u headAcc %u pDOP %u reserved1 %u %u %u' % nums)
				
				fix_type = self.fix_types[nums[10]]
			
			if fix_type == "3d fix":
				no_fix = False
				#print("GPS has 3d fix")
			else:
				#print("GPS has", fix_type)
				pass
		print("GPS has", fix_type)

		
		# 2. ensure pps signal



	def new_thread(self):
		stop_flag = threading.Event()
		thread = threading.Thread(target=self.run, args=(stop_flag,))
		self.threads.append((thread, stop_flag))
		thread.start()
		sleep(0.003)
		if len(self.threads) == 2:
			prevThread, prevFlag = self.threads.pop(0)
			prevFlag.set()
		if len(self.threads) > 2:
			print("Something went wrong with the threading in gyro!")

	def kill_all_threads(self):
		for _, flag in self.threads:
			flag.set()

		print("all GPS threads killed")

	def run(self, flag):
		try:
			file = open(self.wd + str(floor(time())), "wb+")
		except Exception as e:
			print("error opening GPS binary file: ", e)
			print("Exiting GPS thread now")
		return None
		file = open(self.wd + str(floor(time())), "wb+")

		try:
			while not flag.is_set():
				file.write(self.read())
		except Exception as e:
			print("error wrile running GPS: ", e)
			file.close()

		file.close()
		print("finished running GPS thread")

	def read(self):
		out = None
		while out == None:
			out = self.gpsio.ser.sock.recv(8192)
		return out

	def read_file(self, file_name : str):
		assert file_name is str # File name needs to be string
		data = []
		gpsio = gps_io(input_file_name=file_name, read_only=True, write_requested=False, gpsd_host=None)
		while True:
			# this function will print the data to screen, but will not return it
			gpsio.read(decode_func=self.ih.decode_msg)


	def test(self):
		while True:
			print(self.ih.decode_msg(self.read()))

if __name__ == "__main__":
	test = Gps("/home/fissellab/BVEXTracker-main/output/GPS/")

	test.calibrate()
	



