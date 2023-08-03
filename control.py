#!/usr/bin/env python3
from time import sleep, time
import numpy as np
from math import floor
from Sensors.Log import Log

log_filation = open("/home/fissellab/BVEXTracker/Logs/sysLog", "w")
log = Log("CONTROL:", log_filation)
sensor_list = []
calibration_dict = {}
log("test")
log("=======================================\n")
log("beginning control script ... ")

try:
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


from Sensors.Led import LED
led = LED(log_filation)

log("Enabled sensors:" + str([s.name for s in sensor_list]) + "\n")

# in seconds
process_time = 10 #60 * 10

while True:
    # go through each sensor
    num_active_processes = 0

    for sensor in sensor_list:
        # calibration check
        try:
            if not sensor.is_calibrated:
                if not sensor.is_calibrating:
                    if hasattr(sensor, "calibrate"):
                        sensor.calibrate()
                continue
        except Exception as e:
            log("error during calibration of " + sensor.name + ": " + str(e))

        # data collection thread management
        try:
            if len(sensor.processes) == 0: # starts first thread
                sensor.new_process()
            elif time() - sensor.processes[0]["start time"] > process_time: # creates new thread every 60s
                sensor.new_process()
            num_active_processes += 1

        except Exception as e:
            log("error during process management of " + sensor.name + ": " + str(e))

    led.mode = num_active_processes
    sleep(1)

print("\nfinished")
quit()
