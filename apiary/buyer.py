"""This module defines the Buyers used within the CoopHive protocol."""

import json
import logging
import os

import readwrite as rw

from apiary.base_agent import Agent


class NaiveBuyer(Agent):
    """A Buyer in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Buyer instance."""
        super().__init__()
        logging.info("NaiveBuyer initialized")

    def infer(self, states, input_message):
        """Policy of Naive Buyer."""
        output_message = self._preprocess_infer(input_message)
        if output_message == "noop":
            return output_message

        # TODO:
        # Case in which offer comes in, replies with identity here
        # anyone can respond to a non-initial offer with a counteroffer

        # TODO:
        # Case input good offer, output buy attest, use self._somefunctions()

        # TODO:
        # Case input sell_attestation, use self._somefunctions() and output  noop
        return output_message


# TODO:
# def load_states():
# check that states (including p (internal states/model states/policy configurations))
# are up to date and warning if not (not doing anything directly, another process is responsibile for doing something about it).
#     import jax
#     model_pickle = read_pickle('jax_model.pickle')
#     model = jax.from_pickle(model_pickle) # NOTE: This is why we do this in python, even if the training is happening in a completely separate process.
#     return {'X': , ''}
# def infer():
#    match input_message_tag to capute negotiation-strategy-invariant actions and move them to buy/sellagent functions if necessary, else:
#    reply_buy_attest.
#    reply_sell_attest.
#    NOTE: in the case messaging is server-push-based, deal negotiations and job runs are necessarily sequential.


def parse_initial_offer(job_path, price):
    """Parses the initial offer based on the provided job path and price."""
    pubkey = os.getenv("PUBLIC_KEY")
    offerId = "offer_0"  # TODO: make this dynamically assigned based on client/server interaction.
    query = rw.read_as(job_path, "txt")

    data = {
        "_tag": "offer",
        "query": query,
    }

    if price is not None:
        data["price"] = json.loads(price)

    return {"pubkey": pubkey, "offerId": offerId, "data": data}
