#!/bin/bash

# Check for processes using ports 8000 and 8001 and kill them if found
for port in 8000 8001; do
    pid=$(lsof -t -i :"$port")
    if [ -n "$pid" ]; then
        echo "Killing process on port $port with PID: $pid"
        kill -9 "$pid"
    else
        echo "No process found on port $port."
    fi
done

# Get PIDs of processes associated with 'uvicorn' or 'redis'
pids=$(ps aux | grep -E 'uvicorn|redis' | grep -v grep | awk '{print $2}')

# Check if any PIDs were found
if [ -z "$pids" ]; then
    echo "No matching processes found."
else
    # Kill all the found PIDs
    echo "Killing processes with PIDs: $pids"
    kill -9 $pids
fi

# Delete files starting with 'messaging_client_' or 'inference_endpoint_'
echo "Deleting files starting with 'messaging_client_' or 'inference_endpoint_':"
rm -f messaging_client_* inference_endpoint_*

# Check if any files were deleted
if [ $? -eq 0 ]; then
    echo "Files deleted successfully."
else
    echo "No files matching the criteria were found."
fi
