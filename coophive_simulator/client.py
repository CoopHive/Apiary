"""This module defines the Client class used for interacting with solvers and smart contracts within the CoopHive simulator.

The Client class extends the ServiceProvider class and provides methods to manage jobs, 
connect to solvers and smart contracts, handle events, and make decisions regarding matches.
"""

import logging
import os
from collections import deque

from coophive_simulator.deal import Deal
from coophive_simulator.event import Event
from coophive_simulator.globals import global_time
from coophive_simulator.job import Job
from coophive_simulator.log_json import log_json
from coophive_simulator.match import Match
from coophive_simulator.result import Result
from coophive_simulator.service_provider import ServiceProvider
from coophive_simulator.service_provider_local_information import LocalInformation
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.solver import Solver
from coophive_simulator.utils import Tx


class Client(ServiceProvider):
    """A client in the coophive simulator that interacts with solvers and smart contracts to manage jobs and deals.

    Attributes:
        logger (logging.Logger): Logger for the client.
        current_jobs (deque): Queue of current jobs.
        local_information (LocalInformation): Local information instance.
        solver_url (str): URL of the connected solver.
        solver (Solver): Connected solver instance.
        current_deals (dict): Mapping of deal IDs to deals.
        deals_finished_in_current_step (list): List of deals finished in the current step.
        current_matched_offers (list): List of current matched offers.
        T_accept (float): Threshold for accepting matches.
        T_reject (float): Threshold for rejecting matches.
    """

    def __init__(self, address: str):
        """Initialize a new Client instance.

        Args:
            address (str): The address of the client.
        """
        super().__init__(address)
        self.logger = logging.getLogger(f"Client {self.public_key}")
        logging.basicConfig(
            filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
        )
        self.current_jobs = deque()  # TODO: determine the best data structure for this
        self.local_information = LocalInformation()
        self.solver_url = None
        self.solver = None
        self.current_deals: dict[str, Deal] = {}  # maps deal id to deals
        self.deals_finished_in_current_step = []
        self.current_matched_offers: list[Match] = []

    def get_solver(self):
        """Get the connected solver."""
        return self.solver

    def get_smart_contract(self):
        """Get the connected smart contract."""
        return self.smart_contract

    def connect_to_solver(self, url: str, solver: Solver):
        """Connect to a solver and subscribe to its events.

        Args:
            url (str): The URL of the solver.
            solver (Solver): The solver instance to connect to.
        """
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_client(self)

        log_json(self.logger, "Connected to solver", {"solver_url": url})

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        """Connect to a smart contract and subscribe to its events.

        Args:
            smart_contract (SmartContract): The smart contract instance to connect to.
        """
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)

        log_json(self.logger, "Connected to smart contract")

    def add_job(self, job: Job):
        """Add a job to the client's current jobs."""
        self.current_jobs.append(job)

    def get_jobs(self):
        """Get the client's current jobs."""
        return list(self.current_jobs)

    def _agree_to_match(self, match: Match):
        """Agree to a match."""
        client_deposit = match.get_data().get("client_deposit")
        tx = self._create_transaction(client_deposit)
        self.get_smart_contract().agree_to_match(match, tx)

        log_json(self.logger, "Agreed to match", {"match_id": match.get_id()})

    def handle_solver_event(self, event: Event):
        """Handle events from the solver."""
        data = event.get_data()

        if not isinstance(data, Match):
            self.logger.warning(
                f"Unexpected data type received in solver event: {type(data)}"
            )
            log_json(
                self.logger,
                "Received solver event with unexpected data type",
                {"name": event.get_name()},
            )
            return

        # At this point, we know data is of type Match
        event_data = {"name": event.get_name(), "id": data.get_id()}

        log_json(self.logger, "Received solver event", {"event_data": event_data})

        if event.get_name() == "match":
            match = data
            match_data = match.get_data()
            if (
                isinstance(match_data, dict)
                and match_data.get("client_address") == self.get_public_key()
            ):
                self.current_matched_offers.append(match)

    # TODO: Implement this function
    def handle_p2p_event(self, event: Event):
        """P2P handling.

        If the client hears about a resource_offer, it should check if its an appropriate match the way handle_solver_event
        determines that a match exists (if all required machine keys (CPU, RAM) have exactly the same values in both the job offer
        and the resource offer) -> then create a match and append to current_matched_offers.
        """
        pass

    def decide_whether_or_not_to_mediate(self, event: Event):
        """Decide whether to mediate based on the event.

        Args:
            event: The event to decide on.

        Returns:
            bool: True if mediation is needed, False otherwise.
        """
        return True  # for now, always mediate

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

    def update_finished_deals(self):  # TODO: code duplication with resource provider?
        """Update the list of finished deals by removing them from current deals."""
        # remove finished deals from list of current deals and running jobs
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        # clear list of deals finished in current step
        self.deals_finished_in_current_step.clear()

    def make_match_decision(self, match: Match, algorithm):
        """Make a decision on whether to accept, reject, or negotiate a match."""
        if algorithm == "accept_all":
            self._agree_to_match(match)
        elif algorithm == "accept_reject":
            match_utility = self.calculate_utility(match)
            if self.is_only_match(match):
                best_match = self.find_best_match_for_job(match.get_data()["job_offer"])
                # could also check that match_utility > self.T_reject to make it more flexible (basically accept a match if its utility is over T_reject instead of over T_accept)
                # TODO: update where T_accept is accessed from if its moved to job_offer
                if best_match == match and match_utility > match.get_data()["T_accept"]:
                    self._agree_to_match(match)
            else:
                self.reject_match(match)
        elif algorithm == "accept_reject_negotiate":
            #   Negotiate if the utility is within range of being acceptable (between T_reject and T_accept). Call some function negotiate_match
            #   that takes the match as an input and creates a similar but new match where the utility of the new match is > T_accept.
            #   Should be able to handle multiple negotiation rounds.
            #   IMPLEMENT NEGOTIATIONS OVER HTTP: Parameter for how many rounds until negotiation ends (ex: 5).
            best_match = self.find_best_match_for_job(match.get_data()["job_offer"])
            if best_match == match:
                utility = self.calculate_utility(match)
                # TODO: update where T_accept is accessed from if its moved to job_offer
                if utility > match.get_data()["T_accept"]:
                    self._agree_to_match(match)
                # TODO: update where T_reject is accessed from if its moved to job_offer
                elif utility < match.get_data()["T_reject"]:
                    self.reject_match(match)
                else:
                    self.negotiate_match(match)
            else:
                self.reject_match(match)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        # Other considerations:
        #   Check whether there is already a deal in progress for the current job offer, if yes, reject this match.
        #   Introduce a flexibility factor that allows flexibility for when a cient decides to negotiate or reject (manipulates T_reject or utility somehow).
        #       - It allows for some degree of negotiation, making the client less rigid and more adaptable to market conditions.
        #   T_accept and T_reject may be static or dynamically adjusted based on historical data or current market conditions.

    def find_best_match_for_job(self, job_offer_id):
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

    def calculate_utility(self, match: Match):
        """Calculate the utility of a match based on several factors."""
        expected_cost = self.calculate_cost(match)
        expected_benefit = self.calculate_benefit(match)
        return expected_benefit - expected_cost

    # TODO: Implement rejection logic. If a client or compute node rejects a match, it needs to be offered that match again
    # (either via the solver or p2p negotiation) in order to accept it.
    def reject_match(self, match):
        """Reject a match."""
        log_json(self.logger, "Rejected match", {"match_id": match.get_id()})
        pass

    # TODO: Implement negotiation logic. Implement HTTP communication for negotiation
    def negotiate_match(self, match, max_rounds=5):
        """Negotiate a match."""
        log_json(self.logger, "Negotiating match", {"match_id": match.get_id()})
        for _ in range(max_rounds):
            new_match_offer = self.create_new_match_offer(match)
            response = self.communicate_request_to_party(
                match.get_data()["resource_provider_address"], new_match_offer
            )
            if response["accepted"]:
                self._agree_to_match(response["match"])
                return
            match = response["counter_offer"]
        self.reject_match(match)

    def create_new_match_offer(self, match):
        """Create a new match offer with modified terms."""
        data = match.get_data()
        new_data = data.copy()
        new_data["price_per_instruction"] = (
            data["price_per_instruction"] * 0.95
        )  # For example, reduce the price
        new_match = Match(new_data)
        return new_match

    def communicate_request_to_party(self, party_id, match_offer):
        """Communicate a match offer request to a specified party.

        Args:
            party_id: The ID of the party to communicate with.
            match_offer: The match offer details to be communicated.

        Returns:
            dict: A response dictionary indicating acceptance and any counter-offer.
        """
        # Simulate communication - this would need to be implemented with actual P2P or HTTP communication
        response = self.simulate_communication(party_id, match_offer)
        return response

    def simulate_communication(self, party_id, match_offer):
        """Simulate the communication of a match offer to a party and receive a response.

        Args:
            party_id: The ID of the party to communicate with.
            match_offer: The match offer details to be communicated.

        Returns:
            dict: A simulated response including acceptance status and counter-offer.
        """
        log_json(
            self.logger,
            "Simulating communication",
            {"party_id": party_id, "match_offer": match_offer.get_data()},
        )
        # In a real implementation, this function would send a request to the party_id and wait for a response.
        response = {
            "accepted": False,
            "counter_offer": self.create_new_match_offer(match_offer),
        }
        # TODO: update where T_accept is accessed from if its moved to job_offer
        if self.calculate_utility(match_offer) > match_offer.get_data()["T_accept"]:
            response["accepted"] = True
            response["match"] = match_offer
        return response

    def client_loop(self):
        """Process matched offers and update finished deals for the client."""
        for match in self.current_matched_offers:
            self.make_match_decision(match, algorithm="accept_reject_negotiate")
        self.update_finished_deals()
        self.current_matched_offers.clear()
