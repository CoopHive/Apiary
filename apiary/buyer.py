"""This module defines the Buyers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent
from dotenv import load_dotenv

load_dotenv(override=True)


class Naive(Agent):
    """Naive Buyer in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Buyer instance."""
        super().__init__()
        logging.info("Naive Buyer initialized.")

    def _handle_offer(self, input, output):
        """Confirm seller counteroffer."""
        return self._offer_to_buy_attestation(input, output)
