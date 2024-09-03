"""This module defines various utility classes and functions for the CoopHive simulator."""

import hashlib
import json
from dataclasses import dataclass


@dataclass
class Tx:
    """Ethereum transaction metadata."""

    sender: str
    value: float  # [wei]


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
