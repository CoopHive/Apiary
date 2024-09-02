"""This module defines various utility classes and functions for the CoopHive simulator."""

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from coophive.data_attribute import DataAttribute


class AgentType(Enum):
    """Enumeration of different agent types available in the CoopHive ecosystem."""

    RESOURCE_PROVIDER = 1
    CLIENT = 2
    SOLVER = 3
    MEDIATOR = 4
    DIRECTORY = 5


@dataclass
class CID:
    """IPFS CID."""

    hash: str
    data: dict


@dataclass
class Tx:
    """Ethereum transaction metadata."""

    sender: str
    # how many wei
    value: float
    # method: str
    # arguments: []


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


def hash_dict(dict) -> str:
    """Generate a SHA-256 hash of a dictionary.

    Args:
        dict (dict): Dictionary to be hashed.

    Returns:
        str: Hexadecimal representation of the SHA-256 hash.
    """
    hash_function = hashlib.sha256()
    encoded = json.dumps(dict, sort_keys=True).encode()
    hash_function.update(encoded)
    return hash_function.hexdigest()
