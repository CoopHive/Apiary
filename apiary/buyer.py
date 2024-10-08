"""This module defines the Buyers used within the CoopHive protocol."""

import json
import logging
import os
import uuid
from typing import TypedDict, Union

import readwrite as rw

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
                token = str(input_message["data"]["price"][0])
                amount = int(input_message["data"]["price"][1])
                query_cid = self._get_query_cid(input_message)

                statement_uid = apiars.make_buy_statement(
                    token, amount, query_cid, self.private_key
                )

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


class ERC20Token(TypedDict):
    """ERC20."""

    tokenStandard: str
    address: str
    amt: int


class ERC721Token(TypedDict):
    """ERC721."""

    tokenStandard: str
    address: str
    id: int


Token = Union[ERC20Token, ERC721Token]


def create_token(token_data: list) -> Token:
    """Create token object form input token data."""
    token_standard = token_data[0]
    address = token_data[1]

    if token_standard == "ERC20":
        return {"tokenStandard": "ERC20", "address": address, "amt": token_data[2]}
    elif token_standard == "ERC721":
        return {"tokenStandard": "ERC721", "address": address, "id": token_data[2]}
    else:
        raise ValueError(f"Unsupported token standard: {token_standard}")


def parse_initial_offer(job_path, token_data):
    """Parses the initial offer based on the provided job path and price."""
    pubkey = os.getenv("PUBLIC_KEY")
    query = rw.read_as(job_path, "txt")

    data = {
        "_tag": "offer",
        "query": query,
    }

    token_data = json.loads(token_data)
    token = create_token(token_data)

    data["token"] = token

    return {"pubkey": pubkey, "offerId": str(uuid.uuid4()), "data": data}
