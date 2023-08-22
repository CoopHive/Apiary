"""
Test entrypoint script.
"""

# from contract import Contract, ServiceType, Tx, CID
from utils import ServiceType, Tx, CID

import pprint
import random
from machine import Machine
from resource_provider import ResourceProvider
from client import Client
from job import Job
from solver import Solver
from resource_offer import ResourceOffer
from job_offer import JobOffer


class Address:
    def __init__(self):
        self.current_address = 0

    def get_current_address(self):
        return self.current_address

    def increment_current_address(self):
        self.current_address += 1


def main():

    # create solver
    new_solver_1_public_key = "11"
    new_solver_1_url = "http://solver.com"
    new_solver_1 = Solver(new_solver_1_public_key, new_solver_1_url)

    new_resource_provider_1_public_key = 'new_resource_provider_1_public_key'
    new_resource_provider_1 = ResourceProvider(new_resource_provider_1_public_key)
    new_resource_provider_1.connect_to_solver(url=new_solver_1_url, solver=new_solver_1)

    new_client_1_public_key = 'new_client_1_public_key'
    new_client_1 = Client(new_client_1_public_key)
    new_client_1.connect_to_solver(url=new_solver_1_url, solver=new_solver_1)

    new_resource_offer_1 = ResourceOffer()
    new_resource_offer_1.add_data('CPU', '6')
    new_resource_offer_1.add_data('RAM', '3')
    new_resource_offer_1.add_data('owner', new_resource_provider_1_public_key)
    new_resource_offer_1.set_id()
    new_resource_offer_1_id = new_resource_offer_1.get_id()

    new_job_offer_1 = JobOffer()
    new_job_offer_1.add_data('CPU', '6')
    new_job_offer_1.add_data('RAM', '3')
    new_job_offer_1.add_data('owner', new_client_1_public_key)
    new_job_offer_1.set_id()
    new_job_offer_1_id = new_job_offer_1.get_id()

    new_resource_provider_1.get_solver().get_local_information().add_resource_offer(new_resource_offer_1_id, new_resource_offer_1)
    new_client_1.get_solver().get_local_information().add_job_offer(new_job_offer_1_id, new_job_offer_1)

    new_solver_1.solve()

    print(new_solver_1.local_information.get_resource_offers()[new_resource_offer_1_id].get_data().items())
    print(new_solver_1.local_information.get_job_offers()[new_job_offer_1_id].get_data().items())
    new_match_1 = new_solver_1.get_events()[0].get_data()
    print(new_match_1.get_data())
    print(new_match_1.get_id())










if __name__ == "__main__":
    main()

