#!/bin/bash

# Define the ports you want to check
PORTS=(8000 8001)

for PORT in "${PORTS[@]}"; do
  # Find processes using the given port
  PIDS=$(lsof -ti :$PORT)

  # Check if there are any PIDs
  if [ -z "$PIDS" ]; then
    echo "No processes found using port $PORT."
  else
    # Kill all processes using the port
    kill -9 $PIDS

    echo "Processes on port $PORT killed."
  fi
done
