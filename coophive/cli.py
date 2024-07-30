"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import logging
import os

import click
from tqdm import tqdm

from coophive.client import Client
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.utils import Tx, example_offer_data

logger = logging.getLogger(f"test")
logging.basicConfig(
    filename=f"{os.getcwd()}/local_logs", filemode="w", level=logging.DEBUG
)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
)
def cli():
    """Coophive."""
    pass


@cli.command()
def initialize_and_connect_entities():
    """Initializes and connects entities involved in the system.

    This function performs the following actions:
    1. Creates a new smart contract and assigns a public key.
    2. Creates a solver, connects it to the smart contract, and assigns it a public key and URL.
    3. Creates a resource provider, connects it to the solver and the smart contract, and funds the smart contract.
    4. Creates a client, connects it to the solver and the smart contract, and funds the smart contract.
    5. Creates a resource offer and a job offer, adding them to the solver's local information.
    6. Runs the solver for a specified number of steps and updates the job running times for the resource provider.
    """
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
    new_resource_provider_1_public_key = "new_resource_provider_1_public_key"
    new_resource_provider_1 = ResourceProvider(new_resource_provider_1_public_key)
    # resource provider connects to solver
    new_resource_provider_1.connect_to_solver(url=new_solver_1_url, solver=new_solver_1)
    # resource provider connects to smart contract
    new_resource_provider_1.connect_to_smart_contract(
        smart_contract=new_smart_contract_1
    )
    # resource provider adds funds
    tx = Tx(sender=new_resource_provider_1_public_key, value=10)
    new_resource_provider_1.get_smart_contract().fund(tx)

    new_client_1_public_key = "new_client_1_public_key"
    new_client_1 = Client(new_client_1_public_key)
    # client connects to solver
    new_client_1.connect_to_solver(url=new_solver_1_url, solver=new_solver_1)
    # client connects to smart contract
    new_client_1.connect_to_smart_contract(smart_contract=new_smart_contract_1)
    # client adds funds
    tx = Tx(sender=new_client_1_public_key, value=10)
    new_client_1.get_smart_contract().fund(tx)

    new_resource_offer_1 = ResourceOffer()
    new_resource_offer_1.add_data("CPU", "6")
    new_resource_offer_1.add_data("RAM", "3")
    new_resource_offer_1.add_data("owner", new_resource_provider_1_public_key)
    new_resource_offer_1.set_id()
    new_resource_offer_1_id = new_resource_offer_1.get_id()

    new_job_offer_1 = JobOffer()
    new_job_offer_1.add_data("CPU", "6")
    new_job_offer_1.add_data("RAM", "3")
    new_job_offer_1.add_data("owner", new_client_1_public_key)
    new_job_offer_1.set_id()
    new_job_offer_1_id = new_job_offer_1.get_id()

    new_resource_provider_1.get_solver().get_local_information().add_resource_offer(
        new_resource_offer_1_id, new_resource_offer_1
    )
    new_client_1.get_solver().get_local_information().add_job_offer(
        new_job_offer_1_id, new_job_offer_1
    )

    for step in range(2):
        new_solver_1.solve()
        new_resource_provider_1.update_job_running_times()

    logger.info("initialize_and_connect_entities finalized.")


class Addresses:
    """A class to represent and manage addresses."""

    def __init__(self):
        """Initialize the Addresses class with a starting address."""
        self.current_address = 0

    def get_current_address(self):
        """Increment and get the current address as a string."""
        self.increment_current_address()
        return str(self.current_address)

    def increment_current_address(self):
        """Increment the current address counter by 1."""
        self.current_address += 1


def create_resource_provider(
    resource_provider_public_key: str, solver: Solver, smart_contract: SmartContract
):
    """Create a resource provider and connect it to a solver and a smart contract."""
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
    """Create a client and connect it to a solver and a smart contract."""
    client = Client(client_public_key)
    # client connects to solver
    client.connect_to_solver(url=solver.get_url(), solver=solver)
    # client connects to smart contract
    client.connect_to_smart_contract(smart_contract=smart_contract)

    return client


def fund_smart_contract(service_provider, value: float):
    """Fund a smart contract with a specified value."""
    tx = Tx(sender=service_provider.get_public_key(), value=value)
    service_provider.get_smart_contract().fund(tx)


def create_resource_offer(owner_public_key: str):
    """Create a resource offer with example data and an owner public key."""
    resource_offer = ResourceOffer()
    resource_offer.add_data("owner", owner_public_key)
    for data_field, data_value in example_offer_data.items():
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str):
    """Create a job offer with example data and an owner public key."""
    job_offer = JobOffer()
    job_offer.add_data("owner", owner_public_key)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer


@cli.command()
def initialize_simulation_environment():
    """Initializes and runs the simulation environment for the system.

    This function performs the following actions:
    1. Initializes addresses and sets the number of resource providers and clients.
    2. Creates a smart contract and a solver, connecting the solver to the smart contract.
    3. Creates and funds multiple resource providers, connecting them to the solver and the smart contract.
    4. Creates and funds multiple clients, connecting them to the solver and the smart contract.
    5. Creates and registers resource offers for each resource provider.
    6. Creates and registers job offers for each client.
    7. Runs the solver for a specified number of steps, updating resource providers and clients, and performing solver cleanup at each step.
    """
    addresses = Addresses()
    num_resource_providers = (
        1  # TODO: unable to increase this above one for socket port conflicts
    )
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

    new_solver.solve()
    for (
        resource_provider_public_key,
        resource_provider,
    ) in resource_providers.items():
        resource_provider.resource_provider_loop()
    for client_public_key, client in clients.items():
        client.client_loop()

    new_solver.solver_cleanup()
    logger.info("initialize_simulation_environment finalized.")
