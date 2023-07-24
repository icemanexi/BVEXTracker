#!/bin/bash 


is_process_running() {
	pgrep "$1" > /dev/null
}

if is_process_running "startup.sh"; then
	pkill "startup.sh"
else
	echo "startup.sh was not running"
fi

sleep 0.5

if is_process_running "python" && pgrep -f "control.py" > /dev/null; then
	pkill -f "control.py"
else 
	echo "control.py was not running"
fi

echo "done"

