"""This module defines the Sellers used within the CoopHive protocol."""

import logging

from apiary.base_agent import Agent


class NaiveSeller(Agent):
    """A Seller in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Seller instance."""
        super().__init__()
        logging.info("NaiveSeller initialized")

    def infer(self, states, input_messages):
        """Policy of Naive Seller."""
        # TODO:
        # use match to cover all the scheme-compliant cases:
        # https://github.com/CoopHive/redis-scheme-client/blob/main/src/compute-marketplace-scheme.ts#L19
        # define and import functions for cases in which the action is complex.
        # implement exaustive and modular scheme-compliant set of functions for seller.
        # apiars.make_buy_statement()
        pass
