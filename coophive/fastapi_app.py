"""FastAPI application module for handling message-based inference requests."""

import os

from fastapi import Depends, FastAPI

from coophive.buyer import Buyer
from coophive.seller import Seller

role = os.getenv("ROLE", "")
inference_endpoint_url = os.environ[
    "INFERENCE_ENDPOINT_URL"
]  # TODO: use this to specify the inference endpoint port. Needed to simulate two agents and two clients on one machine.

mandatory_states = {
    "private_key": os.getenv("PRIVATE_KEY", ""),
    "public_key": os.getenv("PUBLIC_KEY", ""),
    "policy_name": os.getenv("POLICY_NAME", ""),
}

# FastAPI application
app = FastAPI()


def get_agent():
    """Dependency that provides a configured Agent based on global settings."""
    if role == "seller":
        return Seller(**mandatory_states)
    elif role == "buyer":
        return Buyer(**mandatory_states)


@app.post("/")
async def inference_endpoint(message: dict, agent=Depends(get_agent)):
    """Process a message and return the inference result."""
    return agent.policy.infer(message)
    # message needs to be scheme-compliant, as per:
    # https://github.com/CoopHive/redis-scheme-client/blob/main/src/scheme.ts#L108
