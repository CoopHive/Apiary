"""Manage External Services."""

import os


def start_job_daemon():
    """Start Job Daemon."""
    # TODO: get process_id
    # process_id = subprocess.run()

    # TODO: store it in something like job.lock
    # logging.info(process_id)?
    # if job.lock already there, break and ask user to delete job.lock manually and restart.

    pass


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
