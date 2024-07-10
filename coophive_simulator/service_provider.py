from coophive_simulator.event import Event
from coophive_simulator.utils import *


class ServiceProvider:
    def __init__(self, public_key: str = None):
        self.public_key = public_key
        self.local_information = LocalInformation()
        self.events = []
        self.event_handlers = []

    def get_public_key(self):
        return self.public_key

    def get_local_information(self):
        return self.local_information

    def get_events(self):
        return self.events

    def emit_event(self, event: Event):
        self.events.append(event)
        for event_handler in self.event_handlers:
            event_handler(event)

    def subscribe_event(self, handler):
        self.event_handlers.append(handler)

    # Create a reusable transaction object
    def _create_transaction(self, value):
        """Helper function to create a transaction object."""
        return Tx(sender=self.get_public_key(), value=value)

    # not supporting unsubscribing


class LocalInformation:
    ipfs = IPFS()

    def __init__(self):
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
        print("adding resource offer locally")
        self.resource_offers[id] = data
        print("adding resource offer to IPFS")
        self.ipfs.add(data)

    def add_job_offer(self, id: str, data):
        print("adding job offer locally")
        self.job_offers[id] = data
        print("adding job offer to IPFS")
        self.ipfs.add(data)

    def get_resource_offers(self):
        return self.resource_offers

    def get_job_offers(self):
        return self.job_offers

    def add_resource_provider(self, resource_provider):
        self.resource_providers[resource_provider.get_public_key()] = resource_provider

    def get_resource_providers(self):
        return self.resource_providers

    def add_client(self, client):
        self.clients[client.get_public_key()] = client

    def get_clients(self):
        return self.clients
