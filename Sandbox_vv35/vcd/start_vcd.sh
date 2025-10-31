CURRENT_PID=$$
pkill -f "interactive_vcd.py" | grep -v "$CURRENT_PID" | xargs --no-run-if-empty kill -9
pkill -f "python.*vcd" | grep -v "$CURRENT_PID" | xargs --no-run-if-empty kill -9
