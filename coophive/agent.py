"""This module defines the Agent class.

It manage agents, their policies, their states and their actions.
"""

import logging
import os

from coophive.deal import Deal
from coophive.log_json import log_json
from coophive.match import Match
from coophive.smart_contract import LocalInformation
from coophive.utils import AgentType, Tx


class Agent:
    """A class to represent an Agent.

    Examples of Agents include Clients, Resource Providers, Solvers.
    This class provides methods to manage the Agent's local states, global states, policies
    and training routines.
    """

    def __init__(self, public_key: str = None):
        """Initialize the Agent with a public key."""
        self.public_key = public_key
        self.local_information = LocalInformation()
        self.events = []
        self.event_handlers = []
        self.logger = logging.getLogger(f"Agent {self.public_key}")
        logging.basicConfig(
            filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
        )
        self.solver = None
        self.solver_url = None
        self.smart_contract = None
        self.current_deals: dict[str, Deal] = {}
        self.current_jobs = {}
        self.current_matched_offers = []
        self.deals_finished_in_current_step = []

    def get_public_key(self):
        """Get the public key of the agent."""
        return self.public_key

    def get_local_information(self):
        """Get the local information of the agent."""
        return self.local_information

    def get_events(self):
        """Get the events emitted by the agent."""
        return self.events

    def get_solver(self):
        """Get the connected solver."""
        return self.solver

    def subscribe_event(self, handler):
        """Subscribe an event handler to receive emitted events."""
        self.event_handlers.append(handler)

    def _create_transaction(self, value):
        """Helper function to create a reusable transaction object."""
        return Tx(sender=self.get_public_key(), value=value)

    def connect_to_solver(self, url: str, solver):
        """Connect to a solver and subscribe to its events.

        Args:
            url (str): The URL of the solver.
            solver (Solver): The solver instance to connect to.
        """
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)

        self.solver.get_local_information().add_agent(
            agent_type=AgentType.SOLVER,
            public_key=self.solver.public_key,
            agent=self,
        )
        self.logger.info(f"Connected to solver: {url}")

    def connect_to_smart_contract(self, smart_contract):
        """Connect to a smart contract and subscribe to its events.

        Args:
            smart_contract: The smart contract instance to connect to.
        """
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        self.logger.info("Connected to smart contract")

    def handle_solver_event(self, event):
        """Handle events from the solver."""
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        self.logger.info(f"Received solver event: {event_data}")

        if event.get_name() == "match":
            match = event.get_data()
            if (
                match.get_data()[f"{self.__class__.__name__.lower()}_address"]
                == self.get_public_key()
            ):
                self.current_matched_offers.append(match)

    def reject_match(self, match):
        """Reject a match."""
        self.logger.info(f"Rejected match: {match.get_id()}")

    def negotiate_match(self, match, max_rounds=5):
        """Negotiate a match."""
        match_dict = match.get_data()
        rounds_completed = match_dict["rounds_completed"]
        while rounds_completed < max_rounds:
            new_match_offer = self.create_new_match_offer(match)
            response = self.communicate_request_to_party(new_match_offer)
            if response["accepted"]:
                self._agree_to_match(response["match_offer"])
                return
            match = response["counter_offer"]
            rounds_completed += 1
            match.set_attributes({"rounds_completed": rounds_completed})
        self.reject_match(match)

    def communicate_request_to_party(self, match_offer):
        """Communicate a match offer request to a specified party.

        Args:
            match_offer: The match offer details to be communicated.
        """
        return self.simulate_communication(match_offer)

    def simulate_communication(self, match_offer):
        """Simulate communication."""
        message = f"New match offer: {match_offer.get_data()}"

        response_message = "Your offer has been accepted."

        log_json(
            self.logger,
            "Received response from server",
            {"response_message": response_message},
        )

        response = {
            "accepted": "accepted" in response_message,
            "match_offer": match_offer,
            "counter_offer": self.create_new_match_offer(match_offer),
        }
        return response

    def create_new_match_offer(self, match):
        """Create a new match offer with modified terms.

        Args:
            match (Match): The match object to base the new offer on.

        Returns:
            Match: A new match object.
        """
        data = match.get_data()
        new_data = data.copy()

        # Placeholder identity Policy
        new_data["price_per_instruction"] = data["price_per_instruction"]

        new_match = Match(new_data)
        return new_match

    def update_finished_deals(self):
        """Update the list of finished deals by removing them from the current deals and jobs lists."""
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        self.deals_finished_in_current_step.clear()
