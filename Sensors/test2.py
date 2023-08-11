import smbus
import os
from gpsModule import ubx
from time import time, sleep
ubxt = ubx.ubx()
ubxt.protver = 27.12
i2c_bus = 1
GPS_ADDRESS = 0x42
BYTES_AVAIL_HIGH_REG = 0xFD
BYTES_AVAIL_LOW_REG = 0xFE
READ_STREAM_REG = 0xFF

bus = smbus.SMBus(i2c_bus)
sleep(1)
msg_flag = False
possible_start = False
start = False
buff = b''
recv_bytes = 0


while True:
    try:

        byte_dat = (bus.read_byte_data(GPS_ADDRESS, READ_STREAM_REG)).to_bytes(1, byteorder='little')
        print(byte_dat, end="")
        if recv_bytes > 0:
            recv_bytes -= 1
            buff += byte_dat
        
        if possible_start:
            possible_start = False
            if byte_dat == b'b':  # marks start of new message transmission
                recv_bytes = 98 # recv another xx bytes of data into buffer
                print(buff)
                ubxt.decode_msg(buff)

                buff = b'\xb5b' # add this to buffer as it wasnt added previously

        if byte_dat == b'\xb5' and recv_bytes == 0:
            #print("possible start")
            possible_start = True

    except Exception as e:

        print(e)
        
        pass
