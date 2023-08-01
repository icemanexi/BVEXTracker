import serial
from gpsModule.ubx import ubx
from time import time

ubxt = ubx()

ser = serial.Serial('/dev/serial0', timeout=2, baudrate=38400)

try:
    t0 = time()
    while time() < t0 + 60:
        try:
            out = ser.read_until(b'\xb5b')
            print("-"*30)
            #print(out)
            ubxt.decode_msg(b'\xb5b' + out)
            if b'\x01a\x04' in out[0:6]: # NAV-EOE
                t = int.from_bytes(out[4:8], "little")
                #buf = bytearray(out[4:8])
                #print(t)
        except Exception as e:
            print("handled")
            print(e)
            break
    print("closed")

except Exception as e:
    print("handled")
    print(e)
