#!/usr/bin/env python3

from time import sleep
from Sensors.Gyroscope import Gyro
#from Sensors.GPS import Gps
from Sensors.IMU import IMU
from Sensors.Accelerometer import Accelerometer
from Sensors.Magnetometer import Magnetometer
import numpy as np

gyro = Gyro("/home/fissellab/BVEXTracker-main/output/Gyroscope/")
#gps = Gps("/home/fissellab/BVEXTracker-main/output/GPS/")
imu = IMU("/home/fissellab/BVEXTracker-main/output/IMU/")
acc = Accelerometer("/home/fissellab/BVEXTracker-main/output/Accelerometer/")
mag = Magnetometer("/home/fissellab/BVEXTracker-main/output/Magnetometer/")

sensor_list = [gyro, imu, acc, mag]

for sensor in sensor_list:
    sensor.begin()

sleep(60)
print("saving...")

for sensor in sensor_list:
    sensor.save_data()

for sensor in sensor_list:
    sensor.kill()



print("\nfinished")
