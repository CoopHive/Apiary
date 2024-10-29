"""This module defines the Buyers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent
from dotenv import load_dotenv

load_dotenv(override=True)


class NaiveBuyer(Agent):
    """Naive Buyer in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Buyer instance."""
        super().__init__()
        logging.info("NaiveBuyer initialized.")

    def _handle_offer(self, input_message, output_message):
        """Confirm seller counteroffer."""
        return self._offer_to_buy_attestation(input_message, output_message)


class KalmanBuyer(Agent):
    """Kalman filter-based Buyer in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Buyer instance."""
        super().__init__()
        logging.info("KalmanBuyer initialized.")

    def _handle_offer(self, input_message, output_message):
        """Use Kalman Filter from base class, defining only role locally."""
        return super()._kalman_handle_offer(
            input_message, output_message, is_buyer=True
        )
