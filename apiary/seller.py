"""This module defines the Sellers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent
from dotenv import load_dotenv

load_dotenv(override=True)


class NaiveSeller(Agent):
    """Naive Seller in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Seller instance."""
        super().__init__()
        logging.info("NaiveSeller initialized.")

    def _handle_offer(self, input_message, output_message):
        """Confirm buyer offer with identity counteroffer."""
        return output_message


class KalmanSeller(Agent):
    """Kalman filter-based Seller in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Seller instance."""
        super().__init__()
        logging.info("KalmanSeller initialized.")

    def _handle_offer(self, input_message, output_message):
        """Use Kalman Filter from base class, defining only role locally."""
        return super()._kalman_handle_offer(
            input_message, output_message, is_buyer=False
        )
