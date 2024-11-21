"""This module defines the Sellers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent
from dotenv import load_dotenv

load_dotenv(override=True)


class Naive(Agent):
    """Naive Seller in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Seller instance."""
        super().__init__()
        logging.info("Naive Seller initialized.")

    def _handle_offer(self, input, output):
        """Confirm buyer offer with identity counteroffer."""
        _ = input
        return output
