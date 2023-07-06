#!/usr/bin/env python3
from time import sleep
from Sensors.Gyroscope import Gyro
from Sensors.GPS import Gps
from Sensors.IMU import IMU
from Sensors.Accelerometer import Accelerometer
from Sensors.Magnetometer import Magnetometer
import numpy as np

gyro = Gyro("/home/fissellab/BVEXTracker-main/output/Gyroscope/")
gps = Gps("/home/fissellab/BVEXTracker-main/output/GPS/")
imu = IMU("/home/fissellab/BVEXTracker-main/output/IMU/")
acc = Accelerometer("/home/fissellab/BVEXTracker-main/output/Accelerometer/")
mag = Magnetometer("/home/fissellab/BVEXTracker-main/output/Magnetometer/")

sensor_list = []
#sensor_list.append(gyro)
#sensor_list.append(gps)
sensor_list.append(imu)
#sensor_list.append(acc)
sensor_list.append(mag)

try:
    log = open("/home/fissellab/BVEXTracker-main/Logs" + str(floor(time())), "w+")
except Exception as e:
    print("Error opening log file: ", e)
    log = None

# Calibration
def calibrate(arr):
    if not arr:
        print("No sensors in sensor list")
        return False

    fully_calibrated = False
    for sens in arr: # run calibrate script if it exists
        if hasattr(sens, "calibrate"):
            sens.calibrate()

    while not fully_calibrated: # standby mode until sensors are calibrated
        temp = []
        print("| ", end="")
        for sens in arr:
            temp.append(sens.is_calibrated)
            print(sens.name, sens.is_calibrated, "| ", end="")
        if False not in temp:
           fully_calibrated = True
        print("")
        sleep(1)

    print([a.name for a in arr], " calibrated")
    return True


calibrate(sensor_list)
# can now collect data

print("\nfinished")
