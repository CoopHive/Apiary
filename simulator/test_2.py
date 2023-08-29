"""
Test entrypoint script.
"""

# from contract import Contract, ServiceType, Tx, CID
from utils import ServiceType, Tx, CID

import pprint
import random
from machine import Machine
from service_provider import ServiceProvider
from resource_provider import ResourceProvider
from client import Client
from job import Job
from solver import Solver
from resource_offer import ResourceOffer
from job_offer import JobOffer
from smart_contract import SmartContract

import logging


class Address:
    def __init__(self):
        self.current_address = 0

    def get_current_address(self):
        return self.current_address

    def increment_current_address(self):
        self.current_address += 1


def create_resource_provider(resource_provider_public_key: str, solver: Solver, smart_contract: SmartContract):
    # create resource provider
    resource_provider = ResourceProvider(resource_provider_public_key)
    # resource provider connects to solver
    resource_provider.connect_to_solver(url=solver.get_url(), solver=solver)
    # resource provider connects to smart contract
    resource_provider.connect_to_smart_contract(smart_contract=smart_contract)

    return resource_provider


def create_client(client_public_key: str, solver: Solver, smart_contract: SmartContract):
    client = Client(client_public_key)
    # client connects to solver
    client.connect_to_solver(url=solver.get_url(), solver=solver)
    # client connects to smart contract
    client.connect_to_smart_contract(smart_contract=smart_contract)

    return client


def fund_smart_contract(service_provider, value: float):
    tx = Tx(sender=service_provider.get_public_key(), value=value)
    service_provider.get_smart_contract().fund(tx)


def create_resource_offer(owner_public_key: str):
    resource_offer = ResourceOffer()
    resource_offer.add_data('CPU', '6')
    resource_offer.add_data('RAM', '3')
    resource_offer.add_data('owner', owner_public_key)
    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str):
    job_offer = JobOffer()
    job_offer.add_data('CPU', '6')
    job_offer.add_data('RAM', '3')
    job_offer.add_data('owner', owner_public_key)
    job_offer.set_id()

    return job_offer


def main():

    # create smart contract
    new_smart_contract_1_public_key = "new_smart_contract_1_public_key"
    new_smart_contract_1 = SmartContract(new_smart_contract_1_public_key)

    # create solver
    new_solver_1_public_key = "new_solver_1_public_key"
    new_solver_1_url = "http://solver.com"
    new_solver_1 = Solver(new_solver_1_public_key, new_solver_1_url)
    # solver connects to smart contract
    new_solver_1.connect_to_smart_contract(smart_contract=new_smart_contract_1)

    # create resource provider
    new_resource_provider_1_public_key = 'new_resource_provider_1_public_key'
    new_resource_provider_1 = create_resource_provider(new_resource_provider_1_public_key, new_solver_1, new_smart_contract_1)
    # resource provider adds funds
    new_resource_provider_1_initial_fund = 10
    fund_smart_contract(new_resource_provider_1, new_resource_provider_1_initial_fund)

    # create client
    new_client_1_public_key = 'new_client_1_public_key'
    new_client_1 = create_client(new_client_1_public_key, new_solver_1, new_smart_contract_1)
    # client adds funds
    new_client_1_initial_fund = 10
    fund_smart_contract(new_client_1, new_client_1_initial_fund)

    new_resource_offer_1 = create_resource_offer(new_resource_provider_1_public_key)
    new_resource_offer_1_id = new_resource_offer_1.get_id()

    new_job_offer_1 = create_job_offer(new_client_1_public_key)
    new_job_offer_1_id = new_job_offer_1.get_id()

    new_resource_provider_1.get_solver().get_local_information().add_resource_offer(new_resource_offer_1_id, new_resource_offer_1)
    new_client_1.get_solver().get_local_information().add_job_offer(new_job_offer_1_id, new_job_offer_1)

    for step in range(2):
        new_solver_1.solve()
        new_resource_provider_1.update_job_running_times()








if __name__ == "__main__":
    main()

