"""This module defines the Buyer used within the CoopHive protocol."""

from apiary.agent import Agent


class Buyer(Agent):
    """A Buyer in the CoopHive protocol."""

    def __init__(self, config) -> None:
        """Initialize the Buyer instance."""
        super().__init__(config)

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
