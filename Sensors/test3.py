from time import time, sleep
from numpy import save
from math import floor
import threading
from struct import unpack_from
import subprocess

from gpsModule import ubx, gps_io

gpsd = gps_io(input_speed=38400)

ubxt = ubx.ubx()

while True:
    print(gpsd.ser.sock.recv(8192))
    gpsd.read(ubxt.decode_msg)

