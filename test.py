import serial
import ubx

ubxt = ubx.ubx()



ser = serial.Serial('/dev/serial0', timeout=2, baudrate=38400)

while True:
    out = ser.readline()
    ubx.decode_msg(out)
    print(out)
