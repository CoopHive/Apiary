"""FastAPI application module for handling message-based inference requests."""

import logging
import os
import subprocess
import time

from fastapi import FastAPI

from apiary import agent_registry

# FastAPI application
app = FastAPI()


@app.post("/")
async def inference_endpoint(message: dict):
    """Process a message and return the inference result.

    The inference function defines the behavior of Agents based on predefined Policies within the CoopHive simulator.

    Policies dictate how an Agent interacts with the Schema-compliant messaging scheme (action space), determining its mode of behavior.
    Each policy operates in a stateless manner, meaning that the Agent's actions (inferences) are computed in real-time
    using the current state, without persisting any state in memory.
    """
    agent = agent_registry.get_agent()
    states = agent.load_states()
    return agent.infer(states, message)


def start_inference_endpoint():
    """Start Inference Endpoint."""
    lock_file = f"inference_endpoint_{os.getenv('AGENT_NAME')}.lock"
    if os.path.exists(lock_file):
        with open(lock_file, "r") as file:
            lock_content = file.read()
        logging.warning(
            f"{lock_file} already exists, assuming job_daemon already running at PID {lock_content}"
        )
        return

    command = [
        "uvicorn",
        "apiary.inference:app",
        "--host",
        os.getenv("INFERENCE_ENDPOINT.HOST"),
        "--port",
        str(os.getenv("INFERENCE_ENDPOINT.PORT")),
    ]

    # Start the Uvicorn app and dump the PID to the lock file
    process = subprocess.Popen(command)

    time.sleep(5)

    with open(lock_file, "w") as f:
        f.write(str(process.pid))

    logging.info(f"Inference endpoint started with PID {process.pid}")
