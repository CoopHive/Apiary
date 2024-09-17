"""This module defines the Buyer class used for interacting with solvers and smart contracts within the CoopHive simulator."""

import logging
from collections import deque

from coophive.agent import Agent
from coophive.deal import Deal
from coophive.event import Event
from coophive.match import Match
from coophive.result import Result
from coophive.utils import Tx, log_json


class Buyer(Agent):
    """A Buyer in the coophive protocol."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        policy_name: str,
    ):
        """Initialize a new Buyer instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            policy_name=policy_name,
        )

        self.current_jobs = deque()
        self.current_deals: dict[str, Deal] = {}  # maps deal id to deals

    def handle_server_messages(self):
        """Handle incoming messages from the server."""
        while True:
            try:
                break
                message = message.decode("utf-8")
                logging.info(f"Received message from server: {message}")
                if "New match offer" in message:
                    match_data = eval(message.split("New match offer: ")[1])
                    new_match = Match(match_data)
                    match_dict = new_match.get_data()
                    if "rounds_completed" not in match_dict:
                        new_match["rounds_completed"] = 0
                    for existing_match in self.current_matched_offers:
                        if existing_match.get_id() == new_match.get_id():
                            # Continue negotiating on the existing match
                            self.negotiate_match(existing_match)
                            break
                    else:
                        # New match, add to current_matched_offers and process
                        self.current_matched_offers.append(new_match)
                        self.make_match_decision(new_match)
            except Exception as e:
                logging.info(f"Error handling message: {e}")

    def _agree_to_match(self, match: Match):
        """Agree to a match."""
        buyer_deposit = match.get_data().get("buyer_deposit")
        tx = self._create_transaction(buyer_deposit)
        self.get_smart_contract().agree_to_match(match, tx)

        log_json("Agreed to match", {"match_id": match.get_id()})

    # TODO: transfer functionality inside policy evaluation,
    # the mediation strategy is part of the agent policy.
    def decide_whether_or_not_to_mediate(self, event: Event):
        """Decide whether to mediate based on the event.

        Args:
            event: The event to decide on.

        Returns:
            bool: True if mediation is needed, False otherwise.
        """
        return True  # for now, always mediate

    # TODO: transfer functionality inside policy evaluation,
    # the mediation strategy is part of the agent policy.
    def request_mediation(self, event: Event):
        """Request mediation for an event."""
        log_json("Requesting mediation", {"event_name": event.name})
        self.smart_contract.mediate_result(event)

    def pay_compute_node(self, event: Event):
        """Pay the compute node based on the event result."""
        result = event.get_data()

        if not isinstance(result, Result):
            logging.warning(
                f"Unexpected data type received in solver event: {type(result)}"
            )
        else:
            result_data = result.get_data()
            deal_id = result_data["deal_id"]
            if deal_id in self.current_deals.keys():
                self.smart_contract.deals[deal_id] = self.current_deals.get(deal_id)
                result_instruction_count = result_data["instruction_count"]
                result_instruction_count = float(result_instruction_count)
                price_per_instruction = (
                    self.current_deals.get("deal_123")
                    .get_data()
                    .get("price_per_instruction")
                )
                payment_value = result_instruction_count * price_per_instruction
                log_json(
                    "Paying compute node",
                    {"deal_id": deal_id, "payment_value": payment_value},
                )
                tx = Tx(sender=self.public_key, value=payment_value)

                self.smart_contract.post_buyer_payment(result, tx)
                self.deals_finished_in_current_step.append(deal_id)

    def handle_smart_contract_event(self, event: Event):
        """Handle events from the smart contract."""
        data = event.get_data()

        if isinstance(data, Deal) or isinstance(data, Match):
            event_data = {"name": event.name, "id": data.get_id()}
            log_json("Received smart contract event", {"event_data": event_data})
        else:
            log_json(
                "Received smart contract event with unexpected data type",
                {"name": event.name},
            )

        if isinstance(data, Deal):
            deal = data
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data["buyer_address"] == self.public_key:
                self.current_deals[deal_id] = deal
        elif isinstance(data, Match):
            if event.name == "result":
                # decide whether to mediate result
                mediate_flag = self.decide_whether_or_not_to_mediate(event)
                if mediate_flag:
                    self.request_mediation(event)
                else:
                    self.pay_compute_node(event)

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def find_best_match(self, job_offer_id):
        """Find the best match for a given job offer based on utility."""
        best_match = None
        highest_utility = -float("inf")
        for match in self.current_matched_offers:
            if match.get_data().get("job_offer") == job_offer_id:
                utility = self.calculate_utility(match)
                if utility > highest_utility:
                    highest_utility = utility
                    best_match = match
        return best_match

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def calculate_cost(self, match):
        """Calculate the cost of a match.

        Args:
            match: An object containing the match details.

        Returns:
            float: The cost of the match based on price per instruction and expected number of instructions.
        """
        data = match.get_data()
        price_per_instruction = data.get("price_per_instruction", 0)
        expected_number_of_instructions = data.get("expected_number_of_instructions", 0)
        return price_per_instruction * expected_number_of_instructions

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def calculate_benefit(self, match):
        """Calculate the expected benefit of a match to the Buyer.

        Args:
            match: An object containing the match details.

        Returns:
            float: The expected benefit to the Buyer from the match.
        """
        data = match.get_data()
        expected_benefit_to_buyer = data.get("expected_benefit_to_buyer", 0)
        return expected_benefit_to_buyer

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def calculate_utility(self, match: Match):
        """Calculate the utility of a match based on several factors."""
        expected_cost = self.calculate_cost(match)
        expected_benefit = self.calculate_benefit(match)
        return expected_benefit - expected_cost

    # TODO: the policy inference function shall interact directly with the messaging client.
    # Everything in the make_match_decision should happen inside the policy inference,
    # which is also responsible for outputs to be scheme-compliant.
    # This will deprecate the make_match_decision function.
    def make_match_decision(self, match):
        """Make a decision on whether to accept, reject, or negotiate a match."""
        output_message = self.policy.infer(match)
