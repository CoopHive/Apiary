"""
Test entrypoint script.
"""

from coophive_simulator.client import Client
from coophive_simulator.job_offer import JobOffer
from coophive_simulator.resource_offer import ResourceOffer
from coophive_simulator.resource_provider import ResourceProvider
from coophive_simulator.smart_contract import SmartContract
from coophive_simulator.solver import Solver
from coophive_simulator.utils import Tx


class Address:
    def __init__(self):
        self.current_address = 0

    def get_current_address(self):
        return self.current_address

    def increment_current_address(self):
        self.current_address += 1


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


if __name__ == "__main__":
    main()
