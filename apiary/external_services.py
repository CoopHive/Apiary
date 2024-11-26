"""Manage External Services."""

import json
import logging
import os
import subprocess
import time

import readwrite as rw


def start_job_daemon():
    """Start Job Daemon."""
    try:
        result = subprocess.run(
            ["podman", "machine", "ls", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        machines = json.loads(result.stdout)

        machine_names = [entry["Name"] for entry in machines]

        if "podman-machine-default" in machine_names:
            is_running = bool(
                next(
                    (
                        m["Running"]
                        for m in machines
                        if m["Name"] == "podman-machine-default"
                    ),
                    None,
                )
            )
            logging.info("Podman machine 'podman-machine-default' already exists.")
        else:
            is_running = False
            subprocess.run(["podman", "machine", "init"], check=True)
            logging.info("Podman machine initialized successfully.")

        if not is_running:
            subprocess.run(["podman", "machine", "start"], check=True)
            logging.info("Podman machine started successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error while managing Podman machine: {e}")


def start_messaging_client(initial_offer=None):
    """Start Messaging Client."""
    lock_file = f"messaging_client_{os.getenv('AGENT_NAME')}.lock"
    if os.path.exists(lock_file):
        lock_content = rw.read_as(lock_file, extension="txt")
        logging.warning(
            f"{lock_file} exists, messaging client running at PID {lock_content}"
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

    time.sleep(1)
    rw.write_as(str(process.pid), lock_file, extension="txt")
    logging.info(f"Messaging Client started with PID {process.pid}")


def kill_job_daemon():
    """Kill Job Daemon."""
    pass


def kill_messaging_client():
    """Kill Messaging Client."""
    pass
