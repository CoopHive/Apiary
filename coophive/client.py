"""This module defines the Client class used for interacting with solvers and smart contracts within the CoopHive simulator.

The Client class extends the Agent class and provides methods to manage jobs, 
connect to solvers and smart contracts, handle events, and make decisions regarding matches.
"""

import logging
import socket
import threading
from collections import deque

from coophive.agent import Agent
from coophive.deal import Deal
from coophive.event import Event
from coophive.log_json import log_json
from coophive.match import Match
from coophive.policy import Policy
from coophive.result import Result
from coophive.utils import Tx


class Client(Agent):
    """A client in the coophive simulator that interacts with solvers and smart contracts to manage jobs and deals."""

    def __init__(
        self,
        private_key: str,
        public_key: str,
        policy: Policy,
        auxiliary_states: dict = {},
    ):
        """Initialize a new Client instance."""
        super().__init__(
            private_key=private_key,
            public_key=public_key,
            auxiliary_states=auxiliary_states,
        )
        self.current_jobs = deque()
        self.policy = policy
        self.current_deals: dict[str, Deal] = {}  # maps deal id to deals
        self.client_socket = None
        self.server_address = ("localhost", 1234)
        self.start_client_socket()

    def start_client_socket(self):
        """Start the client socket and connect to the server."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        logging.info("Connected to server")
        threading.Thread(target=self.handle_server_messages, daemon=True).start()

    def handle_server_messages(self):
        """Handle incoming messages from the server."""
        while True:
            try:
                message = self.client_socket.recv(1024)
                if not message:
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
            except ConnectionResetError:
                logging.info("Connection lost. Closing connection.")
                self.client_socket.close()
                break
            except Exception as e:
                self.logger.info(f"Error handling message: {e}")

    def get_jobs(self):
        """Get the client's current jobs."""
        return list(self.current_jobs)

    def _agree_to_match(self, match: Match):
        """Agree to a match."""
        client_deposit = match.get_data().get("client_deposit")
        tx = self._create_transaction(client_deposit)
        self.get_smart_contract().agree_to_match(match, tx)

        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})

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
        log_json(self.logger, "Requesting mediation", {"event_name": event.get_name()})
        self.smart_contract.mediate_result(event)

    def pay_compute_node(self, event: Event):
        """Pay the compute node based on the event result."""
        result = event.get_data()

        if not isinstance(result, Result):
            self.logger.warning(
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
                    self.logger,
                    "Paying compute node",
                    {"deal_id": deal_id, "payment_value": payment_value},
                )
                tx = Tx(sender=self.get_public_key(), value=payment_value)

                self.smart_contract.post_client_payment(result, tx)
                self.deals_finished_in_current_step.append(deal_id)

    def handle_smart_contract_event(self, event: Event):
        """Handle events from the smart contract."""
        data = event.get_data()

        if isinstance(data, Deal) or isinstance(data, Match):
            event_data = {"name": event.get_name(), "id": data.get_id()}
            log_json(
                self.logger, "Received smart contract event", {"event_data": event_data}
            )
        else:
            log_json(
                self.logger,
                "Received smart contract event with unexpected data type",
                {"name": event.get_name()},
            )

        if isinstance(data, Deal):
            deal = data
            deal_data = deal.get_data()
            deal_id = deal.get_id()
            if deal_data["client_address"] == self.get_public_key():
                self.current_deals[deal_id] = deal
        elif isinstance(data, Match):
            if event.get_name() == "result":
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
        """Calculate the expected benefit of a match to the client.

        Args:
            match: An object containing the match details.

        Returns:
            float: The expected benefit to the client from the match.
        """
        data = match.get_data()
        expected_benefit_to_client = data.get("expected_benefit_to_client", 0)
        return expected_benefit_to_client

    # TODO: transfer functionality inside policy evaluation at the agent level.
    def calculate_utility(self, match: Match):
        """Calculate the utility of a match based on several factors."""
        expected_cost = self.calculate_cost(match)
        expected_benefit = self.calculate_benefit(match)
        return expected_benefit - expected_cost

    def make_match_decision(self, match):
        """Make a decision on whether to accept, reject, or negotiate a match."""
        localInfo = self.get_local_information()
        decision, counteroffer = self.policy.infer(match, localInfo)
        if decision == "accept":
            self._agree_to_match(match)
        elif decision == "reject":
            self.reject_match(match)
        elif decision == "negotiate":
            self.negotiate_match(match)
        else:
            raise ValueError(f"Unknown policy decision: {decision}")

    # TODO: move this functionality in the networking model, at the agent level
    # Also resource providers need to be able to filter into the pubsub and
    # act on it.
    def client_loop(self):
        """Process matched offers and update finished deals for the client."""
        for match in self.current_matched_offers:
            self.make_match_decision(match)
        self.update_finished_deals()
        self.current_matched_offers.clear()
