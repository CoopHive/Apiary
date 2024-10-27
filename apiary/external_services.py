"""Manage External Services."""

import json
import logging
import os
import subprocess
import time


def start_job_daemon():
    """Start Job Daemon."""
    os.system("podman machine init")
    os.system("podman machine start")


def start_messaging_client(initial_offer=None):
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
        "" if not initial_offer else json.dumps(initial_offer),
        os.getenv("REDIS_URL"),
    ]

    process = subprocess.Popen(command)

    time.sleep(3)

    with open(lock_file, "w") as f:
        f.write(str(process.pid))

    logging.info(f"Messaging Client started with PID {process.pid}")


def kill_job_daemon():
    """Kill Job Daemon."""
    pass


def kill_messaging_client():
    """Kill Messaging Client."""
    pass
