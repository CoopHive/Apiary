"""This module defines the CLI (Command Line Interface) for the Coophive application."""

import logging
import os

import click

from coophive.client import Client, create_client
from coophive.job_offer import JobOffer
from coophive.resource_offer import ResourceOffer
from coophive.resource_provider import ResourceProvider
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.state.onchain import Addresses
from coophive.utils import (
    Tx,
    create_job_offer,
    create_n_job_offers,
    create_n_resource_offers,
    create_resource_offer,
    fund_smart_contract,
)

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
