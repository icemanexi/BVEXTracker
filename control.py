#!/usr/bin/env python3
from time import sleep, time
import numpy as np
from math import floor
from Sensors.Log import Log

log_filation =  open("/home/fissellab/BVEXTracker/Logs/sysLog", "a")
log = Log("CONTROL:", log_filation)

sensor_list = []
calibration_dict = {}

log("=======================================\n")
log("beginning control script ... ")

try:
    raise
    from Sensors.Gyroscope import Gyro
    gyro = Gyro("/home/fissellab/BVEXTracker/output/Gyroscope/", log_filation)
    sensor_list.append(gyro)
except Exception as e:
    log("FATAL! error importing gyro, not added to senesor list")
    log(str(e))

try:
    from Sensors.GPS import Gps
    gps = Gps("/home/fissellab/BVEXTracker/output/GPS/", log_filation)
    sensor_list.append(gps)
except Exception as e:
    log("FATAL! error importing gps, not added to senesor list")
    log(str(e))
try:
    from Sensors.Accelerometer import Accelerometer
    acc = Accelerometer("/home/fissellab/BVEXTracker/output/Accelerometer/", log_filation)
    sensor_list.append(acc)
except Exception as e:
    log("FATAL! error importing accelerometer, not added to sensor list")
    log(str(e))
    
try:
    from Sensors.Magnetometer import Magnetometer
    mag = Magnetometer("/home/fissellab/BVEXTracker/output/Magnetometer/", log_filation)
    sensor_list.append(mag)
except Exception as e:
    log("FATAL! error importing magnetometer, not added to sensor list")
    log(str(e))

try:
    from Sensors.IMU import IMU
    imu = IMU("/home/fissellab/BVEXTracker/output/IMU/", log_filation)
    sensor_list.append(imu)
except Exception as e:
    log("FATAL!  error importing IMU, not added to sensor list")
    log(str(e))


log("Enabled sensors:" + str([s.name for s in sensor_list]) + "\n")

while True:
    # go through each sensor
    for sensor in sensor_list:
        # calibration check
        try:
            if not sensor.is_calibrated:
                if not sensor.is_calibrating:
                    sensor.calibrate()
                continue
        except Exception as e:
            log("error during calibration of " + sensor.name + ": " + str(e))

        # data collection thread management
        try:
            if len(sensor.threads) == 0: # starts first thread
                sensor.new_thread()
            elif time() - sensor.threads[0]["start time"] > 10: # creates new thread every 60s
                sensor.new_thread()
        except Exception as e:
            log("error during thread management of " + sensor.name + ": " + str(e))

    sleep(1)

asdasd

print("\nfinished")
quit()
