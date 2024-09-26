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
                pass  # Confirm buyer offer with identity counteroffer
            case "buyAttest":
                statement_uid = input_message["data"]["attestation"]

                # apiars.get_buy_statement(statement_uid, private_key)
                def mock_get_buy_statement(statement_uid, private_key):
                    return (
                        "token",
                        1,
                        "arbiter",
                        "bafkreihy4ldvgswp223sirjii2lck4pfvis3aswy65y2xyquudxvwakldy",
                    )

                (token, quantity, arbiter, job_cid) = mock_get_buy_statement(
                    statement_uid, self.private_key
                )

                self._job_cid_to_result_cid(statement_uid, job_cid)

                # 2) Performs job, use self._somefunctions()
                # 3) apiars.submit_and_collect()
                1 / 0
                pass

        return output_message
