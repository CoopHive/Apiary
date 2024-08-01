"""This module provides helper functions for testing purposes.

Functions:
    fund_smart_contract: Fund a smart contract using a transaction from a service provider.
    create_job_offer: Create a job offer with example data.
    create_n_resource_offers: Create a specified number of resource offers for each resource provider.
    create_n_job_offers: Create a specified number of job offers for each client.
"""

from coophive.client import Client
from coophive.job_offer import JobOffer
from coophive.smart_contract import SmartContract
from coophive.solver import Solver
from coophive.utils import Tx, example_offer_data


def fund_smart_contract(service_provider, value: float):
    """Fund a smart contract using a transaction from a service provider.

    Args:
        service_provider (ServiceProvider): The service provider to fund the smart contract.
        value (float): The value of the transaction.
    """
    tx = service_provider._create_transaction(value)
    service_provider.get_smart_contract().fund(tx)


def create_job_offer(owner_public_key: str, created_at):
    """Create a job offer with example data.

    Args:
        owner_public_key (str): The public key of the job offer owner.
        created_at (str): The creation timestamp.

    Returns:
        JobOffer: The created job offer.
    """
    job_offer = JobOffer()
    job_offer.add_data("owner", owner_public_key)
    job_offer.add_data("created_at", created_at)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer


def create_n_resource_offers(
    resource_providers, num_resource_offers_per_resource_provider, created_at
):
    """Create a specified number of resource offers for each resource provider.

    Args:
        resource_providers (dict): A dictionary of resource providers with public keys as keys.
        num_resource_offers_per_resource_provider (int): The number of resource offers to create per resource provider.
        created_at (str): The creation timestamp.
    """
    for _ in range(num_resource_offers_per_resource_provider):
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
    """Create a specified number of job offers for each client.

    Args:
        clients (dict): A dictionary of clients with public keys as keys.
        num_job_offers_per_client (int): The number of job offers to create per client.
        created_at (str): The creation timestamp.
    """
    for _ in range(num_job_offers_per_client):
        for client_public_key, client in clients.items():
            new_job_offer = create_job_offer(client_public_key, created_at)
            new_job_offer_id = new_job_offer.get_id()
            client.get_solver().get_local_information().add_job_offer(
                new_job_offer_id, new_job_offer
            )
