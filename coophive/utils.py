"""This module defines various utility classes and functions for the CoopHive simulator."""

import hashlib
import json
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """Enumeration of different agent types available in the CoopHive ecosystem."""

    RESOURCE_PROVIDER = 1
    CLIENT = 2
    SOLVER = 3
    VALIDATOR = 4


@dataclass
class Tx:
    """Ethereum transaction metadata."""

    sender: str
    value: float  # [wei]


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
