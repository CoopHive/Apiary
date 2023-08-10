from utils import *


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

    def add_service_provider(
            self, service_type: ServiceType, url: str, metadata: dict, address: str):
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers[address] = Service(service_type, url, metadata)
            case ServiceType.CLIENT:
                self.clients[address] = Service(service_type, url, metadata)
            case ServiceType.SOLVER:
                self.solvers[address] = Service(service_type, url, metadata)
            case ServiceType.MEDIATOR:
                self.mediators[address] = Service(service_type, url, metadata)
            case ServiceType.DIRECTORY:
                self.directories[address] = Service(service_type, url, metadata)

    def remove_service_provider(
            self, service_type: ServiceType, address):
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers.pop(address)
            case ServiceType.CLIENT:
                self.clients.pop(address)
            case ServiceType.SOLVER:
                self.solvers.pop(address)
            case ServiceType.MEDIATOR:
                self.mediators.pop(address)
            case ServiceType.DIRECTORY:
                self.directories.pop(address)

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
