#!/bin/bash
cd
git clone https://www.github.com/icemanexi/BVEXTracker
cd BVEXTracker
sudo apt install gspd
sudo pat install chrony
sudo systemctl disable gett@ttyAMA0
sudo apt install python3-gps
sudo apt install pps-tools
sudo systemctl enable gpsd
sudo systemctl start gpsd