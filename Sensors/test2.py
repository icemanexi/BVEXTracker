import smbus
from gpsModule import ubx

ubxt = ubx.ubx()
ubxt.protver = 27.12
i2c_bus = 1
device_address = 0x10
register_address = 0xFF
bus = smbus.SMBus(i2c_bus)
dat = b''
msg_flag = False
while True:
    data = bus.read_byte_data(device_address, register_address)
    if data == 255: #either nothing, or eom
        if msg_flag:
            print(dat)
            ubxt.decode_msg(dat)
            dat = b''
            msg_flag = False
            print("")
        continue
    msg_flag = True
    dat += (data).to_bytes(1, byteorder='little')

# Close the I2C bus
bus.close()

