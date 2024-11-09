#!/bin/bash

# Loop through files that match the patterns
for file in messaging_client_* inference_endpoint_*; do
  # Check if the file exists to avoid errors
  if [[ -f "$file" ]]; then
    # Read the PID from the file
    pid=$(cat "$file")
    
    # Check if the PID is a valid number
    if [[ "$pid" =~ ^[0-9]+$ ]]; then
      # Kill the process
      echo "Killing process with PID: $pid from file: $file"
      kill "$pid"
      
      # Check if the kill command was successful
      if [[ $? -eq 0 ]]; then
        echo "Successfully killed process $pid."
      else
        echo "Failed to kill process $pid. It may not exist."
      fi
    else
      echo "Invalid PID in file: $file"
    fi
  fi
done

# Get PIDs of processes associated with 'uvicorn'
pids=$(ps aux | grep -E 'uvicorn' | grep -v grep | awk '{print $2}')

# Check if any PIDs were found
if [ -z "$pids" ]; then
    echo "No matching processes found."
else
    # Kill all the found PIDs
    echo "Killing processes with PIDs: $pids"
    kill -9 $pids
fi

# Delete files starting with 'messaging_client_' or 'inference_endpoint_'
echo "Deleting lock files"
rm -f messaging_client_* inference_endpoint_*

# Check if any files were deleted
if [ $? -eq 0 ]; then
    echo "Files deleted successfully."
else
    echo "No files matching the criteria were found."
fi
