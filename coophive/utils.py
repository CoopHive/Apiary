"""This module defines various utility classes and functions for the CoopHive simulator.

It includes classes for service types, IPFS integration, and transaction metadata,
as well as functions to create resource and job offers.
"""

from dataclasses import dataclass
from enum import Enum

from coophive.client import Client
from coophive.data_attribute import DataAttribute
from coophive.hash_dict import hash_dict
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.smart_contract import SmartContract
from coophive.solver import Solver


class ServiceType(Enum):
    """Enumeration of different service types available in the CoopHive ecosystem."""

    RESOURCE_PROVIDER = 1
    CLIENT = 2
    SOLVER = 3
    MEDIATOR = 4
    DIRECTORY = 5


@dataclass
class CID:
    """IPFS CID."""

    hash: str
    data: {}
    # TODO: Dictionary expression not allowed in type annotation Use Dict[T1, T2] to indicate a dictionary type


@dataclass
class Tx:
    """Ethereum transaction metadata."""

    sender: str
    # how many wei
    value: float
    # method: str
    # arguments: []


@dataclass
class Service:
    """Data class representing a service.

    Attributes:
        service_type: The type of service.
        url: The URL of the service.
        metadata: Metadata of the service stored as an IPFS CID.
        wallet_address: The wallet address associated with the service.
    """

    service_type: ServiceType
    url: str
    metadata: dict  # metadata will be stored as an IPFS CID
    wallet_address: str


@dataclass
class IPFS:
    """Class representing an IPFS system for storing and retrieving data."""

    def __init__(self):
        """Initialize the IPFS system with an empty data store."""
        self.data = {}

    def add(self, data):
        """Add data to the IPFS system.

        Args:
            data: The data to add, which can be of type DataAttribute or dict.
        """
        # check if data is of type DataAttribute
        if isinstance(data, DataAttribute):
            cid_hash = data.get_id()
            self.data[cid_hash] = data
        # check if data is of type dict
        if isinstance(data, dict):
            cid = CID(hash=hash_dict(data), data=data)
            self.data[cid.hash] = data

    def get(self, cid_hash):
        """Retrieve data from the IPFS system by its CID hash."""
        return self.data[cid_hash]


extra_necessary_match_data = {
    "client_deposit": 5,
    "timeout": 10,
    "timeout_deposit": 3,
    "cheating_collateral_multiplier": 50,
    "price_per_instruction": 1,
    "verification_method": "random",
}


# TODO: make this a generator that generates realistic values
# pull from existing databases online?
example_offer_data = {"CPU": 6, "RAM": 3, "GPU": 1}


def create_resource_offer(owner_public_key: str, created_at=None):
    """Create a resource offer.

    Args:
        owner_public_key: The public key of the offer owner.
        created_at: The creation timestamp of the offer.

    Returns:
        A ResourceOffer object with the given data.
    """
    resource_offer = ResourceOffer()
    resource_offer.add_data("owner", owner_public_key)
    resource_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str, created_at=None):
    """Create a job offer with example data.

    Args:
        owner_public_key (str): The public key of the job offer owner.
        created_at: The creation timestamp of the offer.

    Returns:
        A JobOffer object with the given data.
    """
    job_offer = JobOffer()
    job_offer.add_data("owner", owner_public_key)
    job_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer


def create_resource_provider(
    resource_provider_public_key: str, solver: Solver, smart_contract: SmartContract
):
    """Create a resource provider and connect it to a solver and a smart contract.

    Args:
        resource_provider_public_key (str): The public key of the resource provider.
        solver (Solver): The solver to connect to.
        smart_contract (SmartContract): The smart contract to connect to.

    Returns:
        ResourceProvider: The created resource provider.
    """
    resource_provider = ResourceProvider(resource_provider_public_key)
    resource_provider.connect_to_solver(url=solver.get_url(), solver=solver)
    resource_provider.connect_to_smart_contract(smart_contract=smart_contract)

    return resource_provider


def create_client(
    client_public_key: str, solver: Solver, smart_contract: SmartContract
):
    """Create a client and connect it to a solver and a smart contract.

    Args:
        client_public_key (str): The public key of the client.
        solver (Solver): The solver to connect to.
        smart_contract (SmartContract): The smart contract to connect to.

    Returns:
        Client: The created client.
    """
    client = Client(client_public_key)
    client.connect_to_solver(url=solver.get_url(), solver=solver)
    client.connect_to_smart_contract(smart_contract=smart_contract)

    return client


def fund_smart_contract(service_provider, value: float):
    """Fund a smart contract using a transaction from a service provider.

    Args:
        service_provider (ServiceProvider): The service provider to fund the smart contract.
        value (float): The value of the transaction.
    """
    tx = service_provider._create_transaction(value)
    service_provider.get_smart_contract().fund(tx)


def create_n_resource_offers(
    resource_providers, num_resource_offers_per_resource_provider, created_at
):
    """Create a specified number of resource offers for each resource provider.

    Args:
        resource_providers (dict): A dictionary of resource providers with public keys as keys.
        num_resource_offers_per_resource_provider (int): The number of resource offers to create per resource provider.
        created_at (str): The creation timestamp.
    """
    for _ in range(num_resource_offers_per_resource_provider):
        for (
            resource_provider_public_key,
            resource_provider,
        ) in resource_providers.items():
            new_resource_offer = create_resource_offer(
                resource_provider_public_key, created_at
            )
            new_resource_offer_id = new_resource_offer.get_id()
            resource_provider.get_solver().get_local_information().add_resource_offer(
                new_resource_offer_id, new_resource_offer
            )


def create_n_job_offers(clients, num_job_offers_per_client, created_at):
    """Create a specified number of job offers for each client.

    Args:
        clients (dict): A dictionary of clients with public keys as keys.
        num_job_offers_per_client (int): The number of job offers to create per client.
        created_at (str): The creation timestamp.
    """
    for _ in range(num_job_offers_per_client):
        for client_public_key, client in clients.items():
            new_job_offer = create_job_offer(client_public_key, created_at)
            new_job_offer_id = new_job_offer.get_id()
            client.get_solver().get_local_information().add_job_offer(
                new_job_offer_id, new_job_offer
            )
