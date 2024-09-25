"""This module defines the Sellers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent


class NaiveSeller(Agent):
    """A Seller in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Seller instance."""
        super().__init__()
        logging.info("NaiveSeller initialized")

    def infer(self, states, input_message):
        """Policy of Naive Seller."""
        output_message = self._preprocess_infer(input_message)
        if output_message == "noop":
            return output_message

        match input_message["data"].get("_tag"):
            case "offer":
                # Confirm buyer offer with identity counteroffer ?
                pass
            case "buyAttest":
                # TODO
                # Case input buy attest output sell attest, use self._somefunctions()
                pass

        return output_message
