#!/usr/bin/python3
from time import sleep
from numpy import save
from math import floor
from threading import Thread
try:
	from Sensors.gpsModule import ubx, gps_io
except:
	from gpsModule import ubx, gps_io

class Gps:
	def __init__(self, Write_Directory): #runs upon initialization
		self.wd = Write_Directory
		self.thread = Thread(target=self.run, args=())
		self.alive = True
		self.gpsio = gps_io(input_speed=38400)
		self.ih = ubx.ubx()
		self.data = []

		print("gps initialized")


	def kill(self):
		self.alive=False
		self.thread.join()

	def begin(self):
		self.thread = Thread(target=self.run, args=())
		self.thread.start()

	def run(self):
		while self.alive:
			data += self.read()
			print(report)
			sleep(1)

	def read(self):
		out = None
		while out == None:
			out = self.gpsio.ser.sock.recv(8192)
		return out

	def test(self):


if __name__ == "__main__":
	test = Gps("asd")
	test.begin()

	
