"""This module provides helper functions for testing purposes."""


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
