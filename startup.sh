#!/bin/bash

check_control_script() {
	if ps aux | grep control.py | grep -v grep; then
		return 1
	else
		return 0
	fi
}


while :; do
	if check_control_script > /dev/null; then
		echo "control.py is not running, starting the script.."
		python3 $HOME/BVEXTracker/control.py > $HOME/BVEXTracker/Logs/sysLog & # runs in background

	else
		sleep 0
	fi

	sleep 5 # period of checks
done
