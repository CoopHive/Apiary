"""This module defines the ServiceProvider and LocalInformation classes.

It manage service providers, their local information, events, and transactions.
"""

import logging

from coophive_simulator.event import Event
from coophive_simulator.utils import IPFS, ServiceType, Tx


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
        self.resource_offers = {}
        self.job_offers = {}
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
