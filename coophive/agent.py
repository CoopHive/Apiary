"""This module defines the Agent and LocalInformation classes.

It manage agents, their local information, events, and transactions.
"""

import logging
import os

from coophive.deal import Deal
from coophive.event import Event
from coophive.job_offer import JobOffer
from coophive.log_json import log_json
from coophive.match import Match
from coophive.resource_offer import ResourceOffer
from coophive.utils import IPFS, AgentType, Tx


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

    def emit_event(self, event: Event):
        """Emit an event and notify all subscribed event handlers."""
        self.events.append(event)
        for event_handler in self.event_handlers:
            event_handler(event)

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


class LocalInformation:
    """A class to manage local information of agents, resource offers, and job offers.

    Attributes:
        block_number (int): The block number for the current state.
        resource_providers (dict): Mapping from wallet address to resource provider metadata.
        clients (dict): Mapping from wallet address to client metadata.
        solvers (dict): Mapping from wallet address to solver metadata.
        mediators (dict): Mapping from wallet address to mediator metadata.
        directories (dict): Mapping from wallet address to directory metadata.
        resource_offers (dict): Mapping from offer ID to resource offer data.
        job_offers (dict): Mapping from offer ID to job offer data.
    """

    ipfs = IPFS()

    def __init__(self):
        """Initialize the LocalInformation."""
        self.block_number = 0
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}
        self.resource_offers: dict[str, ResourceOffer] = {}
        self.job_offers: dict[str, JobOffer] = {}

    def add_agent(
        self,
        agent_type: AgentType,
        public_key: str,
        agent: Agent,
    ):
        """Add an agent to the appropriate category based on its type.

        Args:
            agent_type (AgentType): The type of agent.
            public_key (str): The public key of the agent.
            agent (Agent): Agent to add.
        """
        match agent_type:
            case AgentType.RESOURCE_PROVIDER:
                self.resource_providers[public_key] = agent
            case AgentType.CLIENT:
                self.clients[public_key] = agent
            case AgentType.SOLVER:
                self.solvers[public_key] = agent
            case AgentType.MEDIATOR:
                self.mediators[public_key] = agent
            case AgentType.DIRECTORY:
                self.directories[public_key] = agent

    def remove_agent(self, agent_type: AgentType, public_key: str):
        """Remove an agent from the appropriate category based on its type.

        Args:
            agent_type (AgentType): The type of agent.
            public_key (str): The public key of the agent.
        """
        match agent_type:
            case AgentType.RESOURCE_PROVIDER:
                self.resource_providers.pop(public_key)
            case AgentType.CLIENT:
                self.clients.pop(public_key)
            case AgentType.SOLVER:
                self.solvers.pop(public_key)
            case AgentType.MEDIATOR:
                self.mediators.pop(public_key)
            case AgentType.DIRECTORY:
                self.directories.pop(public_key)

    def get_list_of_agents(self, agent_type: AgentType):
        """Get a list of agents of a specific type.

        Args:
            agent_type (AgentType): The type of agent.

        Returns:
            dict: A dictionary of agents with public keys.
        """
        match agent_type:
            case AgentType.RESOURCE_PROVIDER:
                return self.resource_providers
            case AgentType.CLIENT:
                return self.clients
            case AgentType.SOLVER:
                return self.solvers
            case AgentType.MEDIATOR:
                return self.mediators
            case AgentType.DIRECTORY:
                return self.directories

    def add_resource_offer(self, id: str, data):
        """Add a resource offer to the local information and IPFS."""
        logging.info("Adding resource offer locally:")
        self.resource_offers[id] = data
        logging.info("Adding resource offer to IPFS:")
        self.ipfs.add(data)

    def add_job_offer(self, id: str, data):
        """Add a job offer to the local information and IPFS."""
        logging.info("Adding job offer locally:")
        self.job_offers[id] = data
        logging.info("Adding job offer to IPFS:")
        self.ipfs.add(data)

    def get_resource_offers(self):
        """Get the resource offers in the local information."""
        return self.resource_offers

    def get_job_offers(self):
        """Get the job offers in the local information."""
        return self.job_offers

    def add_resource_provider(self, resource_provider):
        """Add a resource provider to the local information."""
        self.resource_providers[resource_provider.get_public_key()] = resource_provider

    def get_resource_providers(self):
        """Get the resource providers in the local information."""
        return self.resource_providers

    def add_client(self, client):
        """Add a client to the local information."""
        self.clients[client.get_public_key()] = client

    def get_clients(self):
        """Get the clients in the local information."""
        return self.clients