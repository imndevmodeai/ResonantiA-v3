#!/bin/bash

# A simple script to manage the ArchE Registry Service

SERVICE_NAME="arche_registry"
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="/tmp/${SERVICE_NAME}.log"
VENV_PATH="./.venv" # Path to the virtual environment
WAITRESS_SERVE_PATH="${VENV_PATH}/bin/waitress-serve"
HOST="127.0.0.1"
PORT="5001"

# Function to find an available port
find_available_port() {
    local port=$1
    while ( lsof -i:$port &>/dev/null ); do
        echo "Port $port is in use. Trying next port..."
        port=$((port + 1))
    done
    echo $port
}

start() {
    if [ ! -f "$WAITRESS_SERVE_PATH" ]; then
        echo "Error: waitress-serve not found at ${WAITRESS_SERVE_PATH}."
        echo "Please ensure the virtual environment is set up and dependencies are installed ('pip install -e .')."
        exit 1
    fi

    if [ -f "$PID_FILE" ]; then
        echo "Service is already running with PID $(cat $PID_FILE)."
        exit 1
    fi

    echo "Finding an available port starting from $PORT..."
    PORT=$(find_available_port $PORT)
    echo "Starting service on port $PORT..."

    # We cd into the directory so waitress can find the module.
    (cd arche_registry && nohup python3 -u -m waitress --host=$HOST --port=$PORT api:app > "$LOG_FILE" 2>&1 &)
    
    PID=$!
    echo $PID > "$PID_FILE"
    sleep 2 # Give it a moment to start
    
    if kill -0 $PID > /dev/null 2>&1; then
        echo "Service started successfully with PID $PID."
        echo "Log file: $LOG_FILE"
        echo "Service is running on http://${HOST}:${PORT}"
        # Save the port for the CLI to use
        echo $PORT > /tmp/${SERVICE_NAME}.port
    else
        echo "Failed to start service. Check log file for details: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Service is not running."
        exit 1
    fi

    PID=$(cat "$PID_FILE")
    echo "Stopping service with PID $PID..."
    kill $PID
    sleep 2

    if kill -0 $PID > /dev/null 2>&1; then
        echo "Failed to stop service gracefully. Forcing..."
        kill -9 $PID
    fi
    
    rm -f "$PID_FILE"
    rm -f "/tmp/${SERVICE_NAME}.port"
    echo "Service stopped."
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID > /dev/null 2>&1; then
            PORT=$(cat /tmp/${SERVICE_NAME}.port)
            echo "Service is RUNNING with PID $PID on port $PORT."
        else
            echo "Service has a PID file but is NOT running. Cleaning up."
            rm -f "$PID_FILE"
            rm -f "/tmp/${SERVICE_NAME}.port"
        fi
    else
        echo "Service is STOPPED."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac 