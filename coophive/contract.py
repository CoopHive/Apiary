"""Python interface representing the CoopHive Ethereum/Solidity smart contract.

It also models enough of Ethereum itself, such as wallets. 
We're ignoring gas for now.
"""

# TODO: Matteo question: are we going to need to start modeling gas fees at a certaint point?

import logging
from enum import Enum

from coophive.log_json import log_json
from coophive.utils import Service, Tx


class ServiceType(Enum):
    """Enumeration of different service types available in the contract."""

    RESOURCE_PROVIDER = 1
    CLIENT = 2
    SOLVER = 3
    MEDIATOR = 4
    DIRECTORY = 5


class Contract:
    """Class representing the smart contract."""

    def __init__(self):
        """Initialize the contract with default values."""
        self.block_number = 0
        # Mapping from wallet address -> amount of LIL # TODO: Matteo question: legacy comment to be removed (LIL)?
        self.wallets = {}
        # For the following service providers, mapping from wallet address -> metadata
        self.resource_providers = {}
        self.clients = {}
        self.solvers = {}
        self.mediators = {}
        self.directories = {}
        self.logger = logging.getLogger("Contract")
        logging.basicConfig(
            filename="contract_logs.log", filemode="w", level=logging.DEBUG
        )

    def match_service_type(self):
        """Match a service type."""
        pass

    def register_service_provider(
        self, service_type: ServiceType, url: str, metadata: dict, tx: Tx
    ):
        """Register a service provider.

        Args:
            service_type: The type of service.
            url: The URL of the service.
            metadata: Metadata of the service.
            tx: The transaction associated with the registration.
        """
        self._before_tx(tx.sender)
        # Only solvers and directories need public internet facing URLs at present

        service_data = {
            "service_type": service_type.name,
            "url": url,
            "metadata": metadata,
            "wallet_address": tx.sender,
        }
        log_json(self.logger, "Register service provider", service_data)

        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                self.resource_providers[tx.sender] = Service(
                    service_type, url, metadata, tx.sender
                )
            case ServiceType.CLIENT:
                self.clients[tx.sender] = Service(
                    service_type, url, metadata, tx.sender
                )
            case ServiceType.SOLVER:
                self.solvers[tx.sender] = Service(
                    service_type, url, metadata, tx.sender
                )
            case ServiceType.MEDIATOR:
                self.mediators[tx.sender] = Service(
                    service_type, url, metadata, tx.sender
                )
            case ServiceType.DIRECTORY:
                self.directories[tx.sender] = Service(
                    service_type, url, metadata, tx.sender
                )

    def _before_tx(self, wallet_address: str):
        """Perform actions required before a transaction."""
        self._maybe_init_wallet(wallet_address)
        self._increment_block_number()

    def _increment_block_number(self):
        """Increment the block number."""
        self.block_number += 1

    def _maybe_init_wallet(self, wallet_address: str):
        """Initialize a wallet if it does not already exist."""
        if wallet_address not in self.wallets:
            self.wallets[wallet_address] = 0

    def unregister_service_provider(self, service_type: ServiceType, tx: Tx):
        """Unregister a service provider.

        Args:
            service_type: The type of service.
            tx: The transaction associated with the unregistration.
        """
        service_data = {"service_type": service_type.name, "wallet_address": tx.sender}
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
