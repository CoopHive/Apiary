from utils import *
# from service_provider import ServiceProvider

class LocalInformation:
    def __init__(self):
        self.block_number = 0
        # For the following service providers, mapping from wallet address -> metadata
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}

    # def add_service_provider(
    #         self, service_type: ServiceType, url: str, metadata: dict, tx: Tx):
    #     match service_type:
    #         case ServiceType.RESOURCE_PROVIDER:
    #             self.resource_providers[tx.sender] = Service(service_type, url, metadata, tx.sender)
    #         case ServiceType.CLIENT:
    #             self.clients[tx.sender] = Service(service_type, url, metadata, tx.sender)
    #         case ServiceType.SOLVER:
    #             self.solvers[tx.sender] = Service(service_type, url, metadata, tx.sender)
    #         case ServiceType.MEDIATOR:
    #             self.mediators[tx.sender] = Service(service_type, url, metadata, tx.sender)
    #         case ServiceType.DIRECTORY:
    #             self.directories[tx.sender] = Service(service_type, url, metadata, tx.sender)
    #
    # def remove_service_provider(
    #         self, service_type: ServiceType, tx: Tx):
    #     match service_type:
    #         case ServiceType.RESOURCE_PROVIDER:
    #             self.resource_providers.pop(tx.sender)
    #         case ServiceType.CLIENT:
    #             self.clients.pop(tx.sender)
    #         case ServiceType.SOLVER:
    #             self.solvers.pop(tx.sender)
    #         case ServiceType.MEDIATOR:
    #             self.mediators.pop(tx.sender)
    #         case ServiceType.DIRECTORY:
    #             self.directories.pop(tx.sender)

    # def add_service_provider(
    #         self, service_type: ServiceType, url: str, metadata: dict, public_key: str):
    #     match service_type:
    #         case ServiceType.RESOURCE_PROVIDER:
    #             self.resource_providers[public_key] = Service(service_type, url, metadata, public_key)
    #         case ServiceType.CLIENT:
    #             self.clients[public_key] = Service(service_type, url, metadata, public_key)
    #         case ServiceType.SOLVER:
    #             self.solvers[public_key] = Service(service_type, url, metadata, public_key)
    #         case ServiceType.MEDIATOR:
    #             self.mediators[public_key] = Service(service_type, url, metadata, public_key)
    #         case ServiceType.DIRECTORY:
    #             self.directories[public_key] = Service(service_type, url, metadata, public_key)

    def add_service_provider(
            self, service_type: ServiceType, public_key: str, service_provider):
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

    def remove_service_provider(
            self, service_type: ServiceType, public_key):
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
