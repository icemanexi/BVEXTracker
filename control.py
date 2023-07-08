#!/usr/bin/env python3
from time import sleep, time
import numpy as np
from math import floor

sensor_list = []
calibration_dict = {}

syslog = open("/home/bvextp1/BVEXTracker/Logs/sysLog", "a")
syslog.write("\n=======================================\n")
syslog.write("\nbeginning control script ... ")
syslog.write("\nTime:" + str(floor(time())))

try:
    raise
    from Sensors.Gyroscope import Gyro
    gyro = Gyro("/home/bvextp1/BVEXTracker/output/Gyroscope/", syslog)
    sensor_list.append(gyro)
except Exception as e:
    syslog.write("\nCONTROL: FATAL! error importing gyro, not added to senesor list")
    syslog.write("\nERROR: " + str(e))

try:
    from Sensors.GPS import Gps
    gps = Gps("/home/bvextp1/BVEXTracker/output/GPS/", syslog)
    sensor_list.append(gps)
except Exception as e:
    syslog.write("\nCONTROL: FATAL! error importing gps, not added to senesor list")
    syslog.write("\nERROR: " + str(e))
try:
    from Sensors.Accelerometer import Accelerometer
    acc = Accelerometer("/home/bvextp1/BVEXTracker/output/Accelerometer/", syslog)
    sensor_list.append(acc)
except Exception as e:
    syslog.write("\nCONTROL: FATAL! error importing accelerometer, not added to sensor list")
    syslog.write("\nERROR: " + str(e))
    
try:
    from Sensors.Magnetometer import Magnetometer
    mag = Magnetometer("/home/bvextp1/BVEXTracker/output/Magnetometer/", syslog)
    sensor_list.append(mag)
except Exception as e:
    syslog.write("\nCONTROL: FATAL! error importing magnetometer, not added to sensor list")
    syslog.write("\nERROR: " + str(e))

try:
    from Sensors.IMU import IMU
    imu = IMU("/home/bvextp1/BVEXTracker/output/IMU/", syslog)
    sensor_list.append(imu)
except Exception as e:
    syslog.write("\nCONTROL: FATAL!  error importing IMU, not added to sensor list")
    syslog.write("\nERROR: " + str(e))


syslog.write("\nEnabled sensors:" + str([s.name for s in sensor_list]) + "\n")


#if not arr:
#    syslog.write("CONTROL: No sensors in sensor list")
#    return False
#
#fully_calibrated = False
#for sens in arr: # run calibrate script if it exists
#    if hasattr(sens, "calibrate"):
#        sens.calibrate()
#
#while not fully_calibrated: # standby mode until sensors are calibrated
#    temp = []
#    print("| ", end="")
#    for sens in arr:
#        temp.append(sens.is_calibrated)
#        print(sens.name, sens.is_calibrated, "| ", end="")
#        calibration_dict.append({})
#    if False not in temp:
#       fully_calibrated = True
#    print("")
#    sleep(1)
#
#syslog.write("\nCONTROL: " + str([a.name for a in arr]) + " calibrated")
#return True

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
            syslog.write("CONTROL: error during calibration of " + sensor.name + ": " + str(e))
            print("CONTROL: error during calibration of " + sensor.name + ": " + str(e))

        # data collection thread management
        try:
            if len(sensor.threads) == 0: # starts first thread
                sensor.new_thread()
            elif time() - sensor.threads[0]["start time"] > 10: # creates new thread every 60s
                sensor.new_thread()
        except Exception as e:
            syslog.write("CONTROL: error during thread management of " + sensor.name + ": " + str(e))
            print("CONTROL: error during thread management of ", sensor.name, ": ",  str(e))

    sleep(1)



print("\nfinished")
quit()
