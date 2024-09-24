"""FastAPI application module for handling message-based inference requests."""

import uvicorn
from fastapi import FastAPI


def start_inference_endpoint(config):
    """Start Inference Endpoint."""
    # TODO:
    # same logic as external_services dumping lock for
    # async support.

    uvicorn.run(
        inference_endpoint.app,
        host=config.inference_endpoint.host,
        port=int(config.inference_endpoint.port),
    )


# FastAPI application
app = FastAPI()


@app.post("/")
async def inference_endpoint(message: dict):
    """Process a message and return the inference result."""
    pass
    # agent = get_agent(config)

    # states = agent.load_states(config)
    # return agent.infer(states, message)
    # message needs to be scheme-compliant, as per:
    # https://github.com/CoopHive/redis-scheme-client/blob/main/src/scheme.ts#L108
