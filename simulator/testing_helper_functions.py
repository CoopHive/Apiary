from utils import Tx
from resource_offer import ResourceOffer
from job_offer import JobOffer
from solver import Solver
from smart_contract import SmartContract
from resource_provider import ResourceProvider
from client import Client


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
    tx = service_provider._create_transaction(value)
    #tx = Tx(sender=service_provider.get_public_key(), value=value)
    service_provider.get_smart_contract().fund(tx)


def create_resource_offer(owner_public_key: str, created_at):
    resource_offer = ResourceOffer()
    resource_offer.add_data('owner', owner_public_key)
    resource_offer.add_data('created_at', created_at)
    for data_field, data_value in example_offer_data.items():
        resource_offer.add_data(data_field, data_value)

    resource_offer.set_id()

    return resource_offer


def create_job_offer(owner_public_key: str, created_at):
    job_offer = JobOffer()
    job_offer.add_data('owner', owner_public_key)
    job_offer.add_data('created_at', created_at)
    for data_field, data_value in example_offer_data.items():
        job_offer.add_data(data_field, data_value)

    job_offer.set_id()

    return job_offer


def create_n_resource_offers(resource_providers, num_resource_offers_per_resource_provider, created_at):
    for _ in range(num_resource_offers_per_resource_provider):
        for resource_provider_public_key, resource_provider in resource_providers.items():
            new_resource_offer = create_resource_offer(resource_provider_public_key, created_at)
            new_resource_offer_id = new_resource_offer.get_id()
            resource_provider.get_solver().get_local_information().add_resource_offer(new_resource_offer_id, new_resource_offer)


def create_n_job_offers(clients, num_job_offers_per_client, created_at):
    for _ in range(num_job_offers_per_client):
        for client_public_key, client in clients.items():
            new_job_offer = create_job_offer(client_public_key, created_at)
            new_job_offer_id = new_job_offer.get_id()
            client.get_solver().get_local_information().add_job_offer(new_job_offer_id, new_job_offer)