"""
The smart contract is a Python interface representing (modelling) the CoopHive
Ethereum / Solidity smart contract (and enough of Ethereum itself, e.g.
wallets).

We're ignoring gas for now.
"""

from dataclasses import dataclass
from enum import Enum
# JSON logging
from log_json import log_json
import logging


class ServiceType(Enum):
    RESOURCE_PROVIDER = 1
    CLIENT = 2
    SOLVER = 3
    MEDIATOR = 4
    DIRECTORY = 5


@dataclass
class CID:
    """
    IPFS CID
    """

    hash: str
    data: {}

@dataclass
class Tx:
    """
    Ethereum transaction metadata
    """
    sender: str
    # how many wei
    value: int


@dataclass
class Service:
    service_type: ServiceType
    url: str
    # metadata will be stored as an ipfs CID
    metadata: dict
    wallet_address: str


class Contract:
    def __init__(self):
        self.block_number = 0
        # Mapping from wallet address -> amount of LIL
        self.wallets = {}
        # For the following service providers, mapping from wallet address -> metadata 
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}
        self.logger = logging.getLogger("Contract")
        logging.basicConfig(filename='contract_logs.log', filemode='w', level=logging.DEBUG)


    def match_service_type(self):
        pass

    def register_service_provider(
            self, service_type: ServiceType, url: str, metadata: dict, tx: Tx):
        self._before_tx(tx.sender)
        # Only solvers and directories need public internet facing URLs at present

        # JSON logging
        service_data = {
            "service_type": service_type.name,
            "url": url,
            "metadata": metadata,
            "wallet_address": tx.sender
        }
        log_json(self.logger, "Register service provider", service_data)


        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.CLIENT:
                self.clients[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.SOLVER:
                self.solvers[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.MEDIATOR:
                self.mediators[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.DIRECTORY:
                self.directories[tx.sender] = Service(service_type, url, metadata, tx.sender)

    def _before_tx(self, wallet_address: str):
        self._maybe_init_wallet(wallet_address)
        self._increment_block_number()

    def _increment_block_number(self):
        self.block_number += 1

    def _maybe_init_wallet(self, wallet_address: str):
        if wallet_address not in self.wallets:
            self.wallets[wallet_address] = 0

    def unregister_service_provider(self, service_type: ServiceType, tx: Tx):

        # JSON logging
        service_data = {
            "service_type": service_type.name,
            "wallet_address": tx.sender
        }
        log_json(self.logger, "Unregister service provider", service_data)
        

        match service_type:
        
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers.pop(tx.sender)
            case ServiceType.CLIENT:
                self.clients.pop(tx.sender)
            case ServiceType.SOLVER:
                self.solvers.pop(tx.sender)
            case ServiceType.MEDIATOR:
                self.mediators.pop(tx.sender)
            case ServiceType.DIRECTORY:
                self.directories.pop(tx.sender)
