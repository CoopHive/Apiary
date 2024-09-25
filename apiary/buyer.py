"""This module defines the Buyer used within the CoopHive protocol."""

import os

import readwrite as rw

from apiary.agent import Agent


class Buyer(Agent):
    """A Buyer in the CoopHive protocol."""

    def __init__(self) -> None:
        """Initialize the Buyer instance."""
        super().__init__()

    # from apiary import apiars
    # TODO: implement exaustive and modular scheme-compliant set of functions for buyer.
    # apiars.make_buy_statement()


# class tmp(Agent):
#     def load_states():
#         import jax
#         model_pickle = read_pickle('jax_model.pickle')
#         model = jax.from_pickle(model_pickle) # NOTE: This is why we do this in python, even if the training is happening in a completely separate process.
#         return {'X': , ''}
#     def infer():
#        match input_message_tag to capute negotiation-strategy-invariant actions and move them to buy/sellagent functions if necessary, else:
#        reply_buy_attest.
#        reply_sell_attest.
# NOTE: in the case messaging is server-push-based, deal negotiations and job runs are necessarily sequential.


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
        data["price"] = price

    return {"pubkey": pubkey, "offerId": offerId, "data": data}
