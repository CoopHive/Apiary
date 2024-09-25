"""Manage External Services."""

import json
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
        with open(lock_file, "r") as file:
            lock_content = file.read()
        logging.warning(
            f"{lock_file} already exists, assuming job_daemon already running at PID {lock_content}"
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


def start_messaging_client(initial_offer=""):
    """Start Messaging Client."""
    lock_file = f"messaging_client_{os.getenv('AGENT_NAME')}.lock"
    if os.path.exists(lock_file):
        with open(lock_file, "r") as file:
            lock_content = file.read()
        logging.warning(
            f"{lock_file} already exists, assuming messaging client already running at PID {lock_content}"
        )
        return

    command = [
        "bun",
        "run",
        "./client/runner.ts",
        os.getenv("ROLE"),
        f"{os.getenv('INFERENCE_ENDPOINT.HOST')}:{os.getenv('INFERENCE_ENDPOINT.PORT')}",
        json.dumps(initial_offer),
        os.getenv("REDIS_URL"),
    ]

    process = subprocess.Popen(command)

    time.sleep(5)

    with open(lock_file, "w") as f:
        f.write(str(process.pid))

    logging.info(f"Messaging Client started with PID {process.pid}")


def kill_job_daemon():
    """Kill Job Daemon."""
    pass


def kill_messaging_client():
    """Kill Messaging Client."""
    pass
