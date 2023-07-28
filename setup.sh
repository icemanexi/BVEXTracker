#!/usr/bin/bash
sudo apt install gspd
sudo pat install chrony
sudo systemctl disable gett@ttyAMA0
sudo apt install python3-gps
sudo apt install pps-tools
sudo systemctl enable gpsd
sudo systemctl start gpsd
sudo apt install vim
curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
cp ~/BVEXTracker/.vimrc ~/.vimrc
