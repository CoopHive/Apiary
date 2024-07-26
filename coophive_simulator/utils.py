"""This module defines various utility classes and functions for the CoopHive simulator.

It includes classes for service types, IPFS integration, and transaction metadata,
as well as functions to create resource and job offers.
"""

import logging
from dataclasses import dataclass
from enum import Enum

from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.hash_dict import hash_dict
from coophive_simulator.job_offer import JobOffer
from coophive_simulator.resource_offer import ResourceOffer


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
            logging.info(data)
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


def create_resource_offer(owner_public_key: str, created_at):
    """Create a resource offer.

    Args:
        owner_public_key: The public key of the owner.
        created_at: The creation timestamp of the offer.

    Returns:
        A ResourceOffer object with the given data.
    """
    resource_offer = ResourceOffer()
    resource_offer.add_data("owner", owner_public_key)
    resource_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        logging.info(data_field, data_value)
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str, created_at):
    """Create a job offer.

    Args:
        owner_public_key: The public key of the owner.
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
