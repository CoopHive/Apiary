"""This module provides the LocalInformation class for managing local service provider information.

The LocalInformation class allows adding, removing, and retrieving service providers, 
as well as managing resource and job offers.
"""

from coophive_simulator.utils import ServiceType


class LocalInformation:
    """A class to manage local information of service providers, resource offers, and job offers.

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

    def __init__(self):
        """Initialize a new LocalInformation instance."""
        self.block_number = 0
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}
        self.resource_offers = {}
        self.job_offers = {}

    def add_service_provider(
        self, service_type: ServiceType, public_key: str, service_provider
    ):
        """Add a service provider to the appropriate category based on service type.

        Args:
            service_type (ServiceType): The type of service provider.
            public_key (str): The public key of the service provider.
            service_provider: Metadata or information about the service provider.
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
        """Remove a service provider from the appropriate category based on service type.

        Args:
            service_type (ServiceType): The type of service provider.
            public_key (str): The public key of the service provider to be removed.
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
        """Get a list of service providers of the specified type.

        Args:
            service_type (ServiceType): The type of service providers to retrieve.

        Returns:
            dict: A dictionary of service providers keyed by public key.
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
        """Add a resource offer to the local information."""
        self.resource_offers[id] = data

    def add_job_offer(self, id: str, data):
        """Add a job offer to the local information."""
        self.job_offers[id] = data

    def get_resource_offers(self):
        """Get all resource offers from the local information."""
        return self.resource_offers

    def get_job_offers(self):
        """Get all job offers from the local information."""
        return self.job_offers
