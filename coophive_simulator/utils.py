from dataclasses import dataclass
from enum import Enum

from coophive_simulator.data_attribute import DataAttribute
from coophive_simulator.hash_dict import hash_dict
from coophive_simulator.job_offer import JobOffer
from coophive_simulator.resource_offer import ResourceOffer


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
    value: float
    # method: str
    # arguments: []


@dataclass
class Service:
    service_type: ServiceType
    url: str
    # metadata will be stored as an ipfs CID
    metadata: dict
    wallet_address: str


class IPFS:
    def __init__(self):
        self.data = {}

    def add(self, data):
        # check if data is of type DataAttribute
        if isinstance(data, DataAttribute):
            cid_hash = data.get_id()
            self.data[cid_hash] = data
        # check if data is of type dict
        if isinstance(data, dict):
            print(data)
            cid = CID(hash=hash_dict(data), data=data)
            self.data[cid.hash] = data

    def get(self, cid_hash):
        return self.data[cid_hash]


extra_necessary_match_data = {
    "client_deposit": 5,
    "timeout": 10,
    "timeout_deposit": 3,
    "cheating_collateral_multiplier": 50,
    "price_per_instruction": 1,
    "verification_method": "random",
}


# todo: make this a generator that generates realistic values
# pull from existing databases online?
example_offer_data = {"CPU": 6, "RAM": 3, "GPU": 1}


def create_resource_offer(owner_public_key: str, created_at):
    resource_offer = ResourceOffer()
    resource_offer.add_data("owner", owner_public_key)
    resource_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        print(data_field, data_value)
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str, created_at):
    job_offer = JobOffer()
    job_offer.add_data("owner", owner_public_key)
    job_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer
