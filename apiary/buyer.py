"""This module defines the Buyers used within the CoopHive protocol."""

import logging

from apiary import apiars
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

        match input_message["data"].get("_tag"):
            case "offer":
                token_standard = str(input_message["data"]["token"][0])
                token_address = str(input_message["data"]["address"][1])

                query_cid = self._get_query_cid(input_message)

                if token_standard == "ERC20":
                    amount = int(input_message["data"]["amt"][2])
                    # TODO: add submodule apiars.erc20.make_buy_statement...
                    statement_uid = apiars.make_buy_statement(
                        token_address, amount, query_cid, self.private_key
                    )
                elif token_standard == "ERC721":
                    token_id = int(input_message["data"]["id"][2])

                    print(token_id)
                else:
                    raise ValueError(f"Unsupported token standard: {token_standard}")

                output_message["data"]["_tag"] = "buyAttest"
                output_message["data"]["attestation"] = statement_uid
            case "sellAttest":
                result_cid = input_message["data"]["result"]
                self._get_result_from_result_cid(result_cid)
                return "noop"

        return output_message


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
