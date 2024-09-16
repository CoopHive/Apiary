"""FastAPI application module for handling message-based inference requests."""

from fastapi import FastAPI

from coophive.messaging import Message
from coophive.seller import Seller

# FastAPI application
app = FastAPI()


@app.post("/messages/")
async def inference_endpoint(message: Message):
    """Process a message and return the inference result."""
    seller = Seller(
        private_key="your_private_key",  # Replace with actual values or pass dynamically
        public_key="your_public_key",
        messaging_client_url="redis://localhost:6379",
        policy_name="your_policy_name",
    )
    return seller.policy.infer(message)
