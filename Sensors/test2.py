import smbus
from gpsModule import ubx
from time import time, sleep
ubxt = ubx.ubx()
ubxt.protver = 27.12
i2c_bus = 1
device_address = 0x42
register_address = 0xFF
bus = smbus.SMBus(i2c_bus)
sleep(1)
msg_flag = False
possible_start = False
start = False
buff = b''

while True:
    #try:
    #    data = bus.read_byte_data(device_address, register_address)
    #    if data != 255:
    #        byte_dat = (data).to_bytes(1, byteorder='little')
    #        buff += byte_dat

    #        if possible_start:
    #            possible_start = False
    #            if byte_dat == b'b':
    #                start = True
    #                # recieved message header
    #                print(buff)
    #                buff = buff[-2:]
    #            else:
    #                start = False

    #        if byte_dat == b'\b5':
    #            possible_start = True
    #        


    #except Exception as e:
    #   pass 



    #if data == 255: #either nothing, or eom
    #    if msg_flag:
    #        print(dat)
    #        ubxt.decode_msg(dat)
    #        dat = b''
    #        msg_flag = False
    #        print("")
    #    continue
    #msg_flag = True
    #dat += (data).to_bytes(1, byteorder='little')

# Close the I2C bus
bus.close()

