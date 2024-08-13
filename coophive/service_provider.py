"""This module defines the ServiceProvider and LocalInformation classes.

It manage service providers, their local information, events, and transactions.
"""

import logging
import os

from coophive.event import Event
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.utils import IPFS, ServiceType, Tx
from coophive.match import Match
from coophive.solver import Solver
from coophive.smart_contract import SmartContract


class ServiceProvider:
    """A class to represent a service provider.

    This class provides methods to manage the service provider's public key,
    local information, events, and event handlers.
    """

    def __init__(self, public_key: str = None):
        """Initialize the ServiceProvider with a public key."""
        self.public_key = public_key
        self.local_information = LocalInformation()
        self.events = []
        self.event_handlers = []
        self.logger = logging.getLogger(f"ServiceProvider {self.public_key}")
        logging.basicConfig(filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG)
        self.solver = None
        self.solver_url = None
        self.smart_contract = None
        self.current_deals: dict[str, Deal] = {} 
        self.current_jobs = {}
        self.current_matched_offers = []
        self.deals_finished_in_current_step = []

    def get_public_key(self):
        """Get the public key of the service provider."""
        return self.public_key

    def get_local_information(self):
        """Get the local information of the service provider."""
        return self.local_information

    def get_events(self):
        """Get the events emitted by the service provider."""
        return self.events

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

    ## REFACTOR:
    def connect_to_solver(self, url: str, solver: Solver):
        self.solver_url = url
        self.solver = solver
        self.solver.subscribe_event(self.handle_solver_event)
        self.solver.get_local_information().add_service_provider(self)
        self.logger.info(f"Connected to solver: {url}")

    def connect_to_smart_contract(self, smart_contract: SmartContract):
        self.smart_contract = smart_contract
        smart_contract.subscribe_event(self.handle_smart_contract_event)
        self.logger.info("Connected to smart contract")

    def handle_solver_event(self, event):
        event_data = {"name": event.get_name(), "id": event.get_data().get_id()}
        self.logger.info(f"Received solver event: {event_data}")

        if event.get_name() == "match":
            match = event.get_data()
            if match.get_data()[f"{self.__class__.__name__.lower()}_address"] == self.get_public_key():
                self.current_matched_offers.append(match)

    def handle_smart_contract_event(self, event):
        # This method will be implemented in the subclasses
        raise NotImplementedError("Subclasses must implement handle_smart_contract_event")

    def make_match_decision(self, match, algorithm):
        if algorithm == "accept_all":
            self._agree_to_match(match)
        elif algorithm == "accept_reject":
            match_utility = self.calculate_utility(match)
            best_match = self.find_best_match(match.get_data()[f"{self.__class__.__name__.lower()}_offer"])
            if best_match == match and match_utility > match.get_data()[f"{self.__class__.__name__.lower()}_offer"]["T_accept"]:
                self._agree_to_match(match)
            else:
                self.reject_match(match)
        elif algorithm == "accept_reject_negotiate":
            best_match = self.find_best_match(match.get_data()[f"{self.__class__.__name__.lower()}_offer"])
            if best_match == match:
                utility = self.calculate_utility(match)
                if utility > match.get_data()[f"{self.__class__.__name__.lower()}_offer"]["T_accept"]:
                    self._agree_to_match(match)
                elif utility < match.get_data()[f"{self.__class__.__name__.lower()}_offer"]["T_reject"]:
                    self.reject_match(match)
                else:
                    self.negotiate_match(match)
            else:
                self.reject_match(match)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def calculate_utility(self, match):
        raise NotImplementedError("Subclasses must implement calculate_utility")

    def reject_match(self, match):
        self.logger.info(f"Rejected match: {match.get_id()}")

    def negotiate_match(self, match, max_rounds=5):
        self.logger.info(f"Negotiating match: {match.get_id()}")
        for _ in range(max_rounds):
            new_match_offer = self.create_new_match_offer(match)
            response = self.communicate_request_to_party(match.get_data()[f"{'client' if isinstance(self, ResourceProvider) else 'resource_provider'}_address"], new_match_offer)
            if response["accepted"]:
                self._agree_to_match(response["match"])
                return
            match = response["counter_offer"]
        self.reject_match(match)

    def communicate_request_to_party(self, party_id, match_offer):
        self.logger.info(f"Communicating request to party: {party_id}")
        return self.simulate_communication(party_id, match_offer)

    def simulate_communication(self, party_id, match_offer):
        raise NotImplementedError("Subclasses must implement simulate_communication")

    def update_finished_deals(self):
        for deal_id in self.deals_finished_in_current_step:
            del self.current_deals[deal_id]
        self.deals_finished_in_current_step.clear()

    def _agree_to_match(self, match: Match):
        raise NotImplementedError("Subclasses must implement _agree_to_match")

    def find_best_match(self, offer_id):
        raise NotImplementedError("Subclasses must implement find_best_match")

    def evaluate_match(self, match):
        raise NotImplementedError("Subclasses must implement evaluate_match")

    def create_new_match_offer(self, match):
        raise NotImplementedError("Subclasses must implement create_new_match_offer")

    # not supporting unsubscribing


class LocalInformation:
    """A class to represent local information of the service provider.

    This class provides methods to manage service providers, resource offers, and job offers.
    """

    ipfs = IPFS()

    def __init__(self):
        """Initialize the LocalInformation."""
        self.block_number = 0
        # For the following service providers, mapping from wallet address -> metadata
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}
        self.resource_offers: dict[str, ResourceOffer] = {}
        self.job_offers: dict[str, JobOffer] = {}
        # self.active_job_offers = {}
        # self.active_resource_offers = {}

    def add_service_provider(
        self,
        service_type: ServiceType,
        public_key: str,
        service_provider: ServiceProvider,
    ):
        """Add a service provider to the local information.

        Args:
            service_type (ServiceType): The type of the service provider.
            public_key (str): The public key of the service provider.
            service_provider (ServiceProvider): The service provider to add.
        """
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers[public_key] = service_provider
            case ServiceType.CLIENT:
                self.clients[public_key] = service_provider
            case ServiceType.SOLVER:
                self.solvers[public_key] = service_provider
            case ServiceType.MEDIATOR:
                self.mediators[public_key] = service_provider
            case ServiceType.DIRECTORY:
                self.directories[public_key] = service_provider

    def remove_service_provider(self, service_type: ServiceType, public_key):
        """Remove a service provider from the local information.

        Args:
            service_type (ServiceType): The type of the service provider.
            public_key (str): The public key of the service provider.
        """
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers.pop(public_key)
            case ServiceType.CLIENT:
                self.clients.pop(public_key)
            case ServiceType.SOLVER:
                self.solvers.pop(public_key)
            case ServiceType.MEDIATOR:
                self.mediators.pop(public_key)
            case ServiceType.DIRECTORY:
                self.directories.pop(public_key)

    def get_list_of_service_providers(self, service_type: ServiceType):
        """Get a list of service providers of a specific type.

        Args:
            service_type (ServiceType): The type of the service providers.

        Returns:
            dict: A dictionary of service providers with public keys.
        """
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                return self.resource_providers
            case ServiceType.CLIENT:
                return self.clients
            case ServiceType.SOLVER:
                return self.solvers
            case ServiceType.MEDIATOR:
                return self.mediators
            case ServiceType.DIRECTORY:
                return self.directories

    def add_resource_offer(self, id: str, data):
        """Add a resource offer to the local information and IPFS."""
        logging.info("adding resource offer locally")
        self.resource_offers[id] = data
        logging.info("adding resource offer to IPFS")
        self.ipfs.add(data)

    def add_job_offer(self, id: str, data):
        """Add a job offer to the local information and IPFS."""
        logging.info("adding job offer locally")
        self.job_offers[id] = data
        logging.info("adding job offer to IPFS")
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
