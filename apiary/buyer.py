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


# NOTE:
# def load_states():
# check that states (including p (internal states/model states/policy configurations))
# are up to date and warning if not (not doing anything directly, another process is responsibile for doing something about it).
#     import jax
#     model_pickle = read_pickle('jax_model.pickle')
#     model = jax.from_pickle(model_pickle) # This is why we do this in python, even if the training is happening in a completely separate process.
#     return {'X': , ''}
#    match input_message_tag to capute negotiation-strategy-invariant actions and move them to buy/sellagent functions if necessary, else:
#    reply_buy_attest.
#    reply_sell_attest.
#    NOTE: in the case messaging is server-push-based, deal negotiations and job runs are necessarily sequential.
