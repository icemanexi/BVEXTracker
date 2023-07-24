#!/usr/bin/bash

check_control_script() {
	if ps aux | grep control.py | grep -v grep; then
		return 1
	else
		return 0
	fi
}


while :; do
	if check_control_script; then
		echo "control.py is not running, starting the script.."
		python3 $HOME/BVEXTracker/control.py & # runs in background

	else
		echo "control.py is running"
	fi

	sleep 5 # period of checks
done




