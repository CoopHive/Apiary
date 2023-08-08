"""
The smart contract is a Python interface representing (modelling) the Lilypad
Ethereum / Solidity smart contract (and enough of Ethereum itself, e.g.
wallets).

We're ignoring gas for now.
"""

from dataclasses import dataclass
from enum import Enum


class ServiceType(Enum):
    RESOURCE_PROVIDER = 1
    JOB_CREATOR = 2
    SOLVER = 3
    MEDIATOR = 4
    DIRECTORY = 5


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
        self.job_creators = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}

    def register_service_provider(
            self, service_type: ServiceType, url: str, metadata: dict, tx: Tx):
        self._before_tx(tx.sender)
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.JOB_CREATOR:
                self.job_creators[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.SOLVER:
                self.solvers[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.MEDIATOR:
                self.mediators[tx.sender] = Service(service_type, url, metadata, tx.sender)
            case ServiceType.DIRECTORY:
                self.directories[tx.sender] = Service(service_type, url, metadata, tx.sender)

    def _before_tx(self, wallet_address: str):
        self._maybe_init_wallet(wallet_address)
        self.block_number += 1

    def _increment_block_number(self):
        self.block_number += 1

    def _maybe_init_wallet(self, wallet_address: str):
        if wallet_address not in self.wallets:
            self.wallets[wallet_address] = 0

