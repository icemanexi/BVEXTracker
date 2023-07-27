import smbus

# I2C bus number (often 1 on Raspberry Pi, check with 'i2cdetect -l' command)
i2c_bus = 1

# I2C device address
device_address = 0x20

# Register address to read from
register_address = 0xFF

# Open the I2C bus
bus = smbus.SMBus(i2c_bus)

# Read a single byte from the specified register

dat = b''
msg_flag = False
while True:
    data = bus.read_byte_data(device_address, register_address)
    if data == 255: #either nothing, or eom
        if msg_flag:
            print(dat.decode("unicode_escape"))
            dat = b''
            msg_flag = False
        continue
    msg_flag = True
    dat += (data).to_bytes(1, byteorder='little')

# Close the I2C bus
bus.close()

