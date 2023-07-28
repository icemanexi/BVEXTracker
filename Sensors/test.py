import serial
from gpsModule.ubx import ubx

ubxt = ubx()

ser = serial.Serial('/dev/serial0', timeout=2, baudrate=38400)

while True:
    out = ser.read_until(b'\xb5b')
    if out[0] != ord('$'):
        print("-"*30)
        print(out)
        ubxt.decode_msg(b'\xb5b' + out)
        

