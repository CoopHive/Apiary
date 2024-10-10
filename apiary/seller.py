"""This module defines the Sellers used within the CoopHive protocol."""

import logging

from apiary import apiars
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
                pass  # Confirm buyer offer with identity counteroffer
            case "buyAttest":
                statement_uid = input_message["data"]["attestation"]

                token_standard = str(input_message["data"]["token"]["tokenStandard"])

                if token_standard == "ERC20":
                    (token, quantity, arbiter, job_cid) = (
                        apiars.erc20.get_buy_statement(statement_uid, self.private_key)
                    )

                    result_cid = self._job_cid_to_result_cid(statement_uid, job_cid)

                    sell_uid = apiars.erc20.submit_and_collect(
                        statement_uid, result_cid, self.private_key
                    )
                elif token_standard == "ERC721":
                    (token, token_id, arbiter, job_cid) = (
                        apiars.erc721.get_buy_statement(statement_uid, self.private_key)
                    )

                    result_cid = self._job_cid_to_result_cid(statement_uid, job_cid)

                    sell_uid = apiars.erc721.submit_and_collect(
                        statement_uid, result_cid, self.private_key
                    )
                else:
                    raise ValueError(f"Unsupported token standard: {token_standard}")

                output_message["data"]["_tag"] = "sellAttest"
                output_message["data"]["result"] = result_cid
                output_message["data"]["attestation"] = sell_uid

        return output_message
