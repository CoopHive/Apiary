"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import logging
import os

import click

from coophive.client import Client
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.state.onchain import Addresses
from coophive.utils import Tx, create_job_offer, create_resource_offer

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

    # TODO: unable to increase this above one for socket port conflicts
    num_resource_providers = 1

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


def create_n_resource_offers(
    resource_providers, num_resource_offers_per_resource_provider, created_at
):
    """Creates a specified number of resource offers for each resource provider."""
    for _ in range(num_resource_offers_per_resource_provider):
        logger.info(f"resource test {_}")
        for (
            resource_provider_public_key,
            resource_provider,
        ) in resource_providers.items():
            new_resource_offer = create_resource_offer(
                resource_provider_public_key, created_at
            )
            new_resource_offer_id = new_resource_offer.get_id()
            resource_provider.get_solver().get_local_information().add_resource_offer(
                new_resource_offer_id, new_resource_offer
            )


def create_n_job_offers(clients, num_job_offers_per_client, created_at):
    """Creates a specified number of job offers for each client."""
    for _ in range(num_job_offers_per_client):
        for client_public_key, client in clients.items():
            new_job_offer = create_job_offer(client_public_key, created_at)
            new_job_offer_id = new_job_offer.get_id()
            client.get_solver().get_local_information().add_job_offer(
                new_job_offer_id, new_job_offer
            )


@cli.command()
def run_test_simulation():
    """Runs a test simulation for a smart contract and solver interaction with resource providers and clients.

    The function performs the following steps:
    1. Initializes a smart contract and solver.
    2. Creates resource providers and clients, each with initial funding.
    3. Executes multiple test loops where:
       a. Resource and job offers are created.
       b. The solver processes the offers.
       c. Resource providers and clients are updated.
       d. The smart contract is updated.
       e. The solver performs cleanup operations.
    """
    addresses = Addresses()

    # TODO: unable to increase this above one for socket port conflicts
    num_resource_providers = 1

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

    step = 0

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
        create_n_job_offers(clients, num_job_offers_per_client, current_time_step_str)
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

    logger.info("run_test_simulation finalized.")
