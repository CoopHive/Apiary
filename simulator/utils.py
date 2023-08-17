from dataclasses import dataclass
from enum import Enum


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
