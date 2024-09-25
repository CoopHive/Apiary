"""Manage External Services."""

import logging
import os
import platform
import subprocess
import time


def start_job_daemon():
    """Start Job Daemon."""
    lock_file = "job_daemon.lock"

    # Check if the lock file already exists
    if os.path.exists(lock_file):
        logging.warning(
            f"{lock_file} already exists, assuming job_daemon already running."
        )
        return
    # Determine the operating system
    operating_system = platform.system()

    # Command to start Docker daemon based on the OS
    if operating_system == "Linux":
        docker_command = ["sudo", "dockerd"]
    elif operating_system == "Darwin":
        docker_command = ["open", "-a", "Docker"]
    else:
        raise ValueError(
            "Unsupported operating system. Only Linux, and macOS are supported."
        )

    # Start Docker daemon and dump the PID to the lock file
    process = subprocess.Popen(docker_command)

    time.sleep(5)

    # Write the PID to the lock file
    with open(lock_file, "w") as f:
        f.write(str(process.pid))

    logging.info(f"Docker daemon started with PID {process.pid}")


def start_messaging_client():
    """Start Messaging Client."""
    _ = os.getenv("REDIS_URL")
    pass


def kill_job_daemon():
    """Kill Job Daemon."""
    pass


def kill_messaging_client():
    """Kill Messaging Client."""
    pass
