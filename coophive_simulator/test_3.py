import logging
import os

from coophive_simulator.client import Client
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


def create_n_resource_offers(
    resource_providers, num_resource_offers_per_resource_provider, created_at
):
    for _ in range(num_resource_offers_per_resource_provider):
        logger.info(f"resource test {_}")
        for (
            resource_provider_public_key,
            resource_provider,
        ) in resource_providers.items():
            logger.info(resource_provider_public_key, resource_provider)
            new_resource_offer = create_resource_offer(
                resource_provider_public_key, created_at
            )
            new_resource_offer_id = new_resource_offer.get_id()
            resource_provider.get_solver().get_local_information().add_resource_offer(
                new_resource_offer_id, new_resource_offer
            )


def create_n_job_offers(clients, num_job_offers_per_client, created_at):
    for _ in range(num_job_offers_per_client):
        logger.info(f"job test {_}")
        for client_public_key, client in clients.items():
            new_job_offer = create_job_offer(client_public_key, created_at)
            new_job_offer_id = new_job_offer.get_id()
            client.get_solver().get_local_information().add_job_offer(
                new_job_offer_id, new_job_offer
            )


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
        new_resource_provider_initial_fund = 200
        fund_smart_contract(new_resource_provider, new_resource_provider_initial_fund)

    for _ in range(num_clients):
        # create client
        new_client_public_key = addresses.get_current_address()
        new_client = create_client(
            new_client_public_key, new_solver, new_smart_contract
        )
        # client adds funds
        new_client_initial_fund = 100
        fund_smart_contract(new_client, new_client_initial_fund)

    num_resource_offers_per_resource_provider = 1
    resource_providers = new_solver.get_local_information().get_resource_providers()

    num_job_offers_per_client = 1
    clients = new_solver.get_local_information().get_clients()

    for step in range(5):
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~test loop {step} started~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        current_time_step_str = str(step)
        if step < 3:
            create_n_resource_offers(
                resource_providers,
                num_resource_offers_per_resource_provider,
                current_time_step_str,
            )
            create_n_job_offers(
                clients, num_job_offers_per_client, current_time_step_str
            )
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~solver solving~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        new_solver.solve()
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~solver finished solving~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~updating resource providers~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        for (
            resource_provider_public_key,
            resource_provider,
        ) in resource_providers.items():
            resource_provider.resource_provider_loop()
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~finished updating resource providers~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~updating clients~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        for client_public_key, client in clients.items():
            client.client_loop()
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~finished updating clients~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~updating smart contract~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        new_smart_contract._smart_contract_loop()
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~finished updating smart contract~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~solver cleaning up~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")
        new_solver.solver_cleanup()
        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~solver finished cleaning up~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")

        logger.info("")
        logger.info(
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~test loop {step} completed~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        )
        logger.info("")


if __name__ == "__main__":
    main()
