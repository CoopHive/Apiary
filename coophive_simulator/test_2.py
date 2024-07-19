import logging
import os

from coophive_simulator.client import Client
from coophive_simulator.job_offer import JobOffer
from coophive_simulator.resource_offer import ResourceOffer
from coophive_simulator.resource_provider import ResourceProvider
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.solver import Solver
from coophive_simulator.utils import *

logger = logging.getLogger(f"test")
logging.basicConfig(
    filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
)


class Addresses:
    def __init__(self):
        self.current_address = 0

    def get_current_address(self):
        self.increment_current_address()
        return str(self.current_address)

    def increment_current_address(self):
        self.current_address += 1


def create_resource_provider(
    resource_provider_public_key: str, solver: Solver, smart_contract: SmartContract
):
    # create resource provider
    resource_provider = ResourceProvider(resource_provider_public_key)
    # resource provider connects to solver
    resource_provider.connect_to_solver(url=solver.get_url(), solver=solver)
    # resource provider connects to smart contract
    resource_provider.connect_to_smart_contract(smart_contract=smart_contract)

    return resource_provider


def create_client(
    client_public_key: str, solver: Solver, smart_contract: SmartContract
):
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
    resource_offer.add_data("owner", owner_public_key)
    for data_field, data_value in example_offer_data.items():
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str):
    job_offer = JobOffer()
    job_offer.add_data("owner", owner_public_key)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer


def main():

    addresses = Addresses()
    num_resource_providers = 5
    num_clients = 5

    # create smart contract
    new_smart_contract_public_key = addresses.get_current_address()
    new_smart_contract = SmartContract(new_smart_contract_public_key)

    # create solver
    new_solver_public_key = addresses.get_current_address()
    new_solver_url = "http://solver.com"
    new_solver = Solver(new_solver_public_key, new_solver_url)
    # solver connects to smart contract
    new_solver.connect_to_smart_contract(smart_contract=new_smart_contract)

    for _ in range(num_resource_providers):
        # create resource provider
        new_resource_provider_public_key = addresses.get_current_address()
        new_resource_provider = create_resource_provider(
            new_resource_provider_public_key, new_solver, new_smart_contract
        )
        # resource provider adds funds
        # new_resource_provider_1_initial_fund = 10
        # new_resource_provider_1_initial_fund = random.randint(0, 1000)
        new_resource_provider_initial_fund = 100
        fund_smart_contract(new_resource_provider, new_resource_provider_initial_fund)

    for _ in range(num_clients):
        # create client
        new_client_public_key = addresses.get_current_address()
        new_client = create_client(
            new_client_public_key, new_solver, new_smart_contract
        )
        # client adds funds
        new_client_initial_fund = 10
        fund_smart_contract(new_client, new_client_initial_fund)

    resource_providers = new_solver.get_local_information().get_resource_providers()
    for resource_provider_public_key, resource_provider in resource_providers.items():
        new_resource_offer = create_resource_offer(resource_provider_public_key)
        new_resource_offer_id = new_resource_offer.get_id()
        resource_provider.get_solver().get_local_information().add_resource_offer(
            new_resource_offer_id, new_resource_offer
        )

    clients = new_solver.get_local_information().get_clients()
    for client_public_key, client in clients.items():
        new_job_offer = create_job_offer(client_public_key)
        new_job_offer_id = new_job_offer.get_id()
        client.get_solver().get_local_information().add_job_offer(
            new_job_offer_id, new_job_offer
        )

    for step in range(2):
        new_solver.solve()
        # todo iterate over all resource providers
        for (
            resource_provider_public_key,
            resource_provider,
        ) in resource_providers.items():
            resource_provider.resource_provider_loop()
        for client_public_key, client in clients.items():
            client.client_loop()
        new_solver.solver_cleanup()

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~test loop {step} completed~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")


if __name__ == "__main__":
    main()
