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
    # contract = Contract()
    #
    # address = Address()
    #
    # def create_new_address():
    #     if len(contract.wallets) != 0:
    #         Address.increment_current_address(address)
    #     return hex(Address.get_current_address(address))
    #     # return Address.get_current_address(address)

    # for _ in range(2):
    #     contract.register_service_provider(
    #         ServiceType.SOLVER,
    #         "http://foo1.com",
    #         {"labels": ["local-test"]},
    #         Tx(create_new_address(), 0)
    #     )
    #
    #     contract.register_service_provider(
    #         ServiceType.DIRECTORY,
    #         "http://foo2.com",
    #         {"labels": ["local-test"]},
    #         Tx(create_new_address(), 0)
    #     )
    #
    #     contract.register_service_provider(
    #         ServiceType.CLIENT,
    #         "",
    #         {"labels": ["local-test"]},
    #         Tx(create_new_address(), 0)
    #     )
    #
    #     contract.register_service_provider(
    #         ServiceType.RESOURCE_PROVIDER,
    #         "",
    #         {"labels": ["local-test"]},
    #         Tx(create_new_address(), 0)
    #     )
    #
    #     contract.register_service_provider(
    #         ServiceType.MEDIATOR,
    #         "",
    #         {"labels": ["local-test"]},
    #         Tx(create_new_address(), 0)
    #     )
    #
    #
    #
    # def get_list_of_service_providers(service_type: ServiceType):
    #     match service_type:
    #         case ServiceType.RESOURCE_PROVIDER:
    #             return contract.resource_providers
    #         case ServiceType.CLIENT:
    #             return contract.clients
    #         case ServiceType.SOLVER:
    #             return contract.solvers
    #         case ServiceType.MEDIATOR:
    #             return contract.mediators
    #         case ServiceType.DIRECTORY:
    #             return contract.directories
    #
    # print("--> block_number")
    # pprint.pprint(contract.block_number)
    # print("--> wallets")
    # pprint.pprint(contract.wallets)
    #
    # print("--> resource_providers")
    # pprint.pprint(get_list_of_service_providers(ServiceType.RESOURCE_PROVIDER))
    # print("--> clients")
    # pprint.pprint(get_list_of_service_providers(ServiceType.CLIENT))
    # print("--> solvers")
    # pprint.pprint(get_list_of_service_providers(ServiceType.SOLVER))
    # print("--> directories")
    # pprint.pprint(get_list_of_service_providers(ServiceType.DIRECTORY))
    # print("--> mediators")
    # pprint.pprint(get_list_of_service_providers(ServiceType.MEDIATOR))
    #
    # mediators = get_list_of_service_providers(ServiceType.MEDIATOR)
    # some_mediator_address = random.choice(list(mediators.keys()))
    # print(f'mediator being removed: {some_mediator_address}')
    # contract.unregister_service_provider(
    #     ServiceType.MEDIATOR,
    #     Tx(some_mediator_address, 0))
    #
    # print("--> mediators after removing mediator")
    # pprint.pprint(get_list_of_service_providers(ServiceType.MEDIATOR))

    # machine_attributes = {'CPU', 'RAM'}
    # new_machine_1 = Machine(machine_attributes)
    new_machine_1 = Machine()
    new_machine_1.add_data('CPU', '4')
    new_machine_1.add_data('RAM', '2')
    # should throw exception if GPU is not one of the machine attributes
    # new_machine_1.add_data('GPU', '3090')
    machine_data = new_machine_1.get_machine_data()
    print(machine_data)

    # new_machine_2 = Machine(machine_attributes)
    new_machine_2 = Machine()
    new_machine_2.add_data('CPU', '8')
    new_machine_2.add_data('RAM', '4')

    new_resource_provider_1_url = ""
    new_resource_provider_1_public_key = 'new_resource_provider_1_public_key'
    new_resource_provider_1 = ResourceProvider(new_resource_provider_1_public_key, new_resource_provider_1_url)
    new_machine_1_CID = CID('new_machine_1_CID', {})
    new_machine_2_CID = CID('new_machine_2_CID', {})
    new_resource_provider_1.add_machine(new_machine_1_CID, new_machine_1)
    new_resource_provider_1.add_machine(new_machine_2_CID, new_machine_2)
    resource_provider_machines = new_resource_provider_1.get_machines()
    print(resource_provider_machines)
    # should match above
    print(resource_provider_machines[new_machine_1_CID.hash].get_machine_data())
    print(resource_provider_machines[new_machine_2_CID.hash].get_machine_data())

    print(resource_provider_machines[new_machine_1_CID.hash].get_machine_uuid())
    print(resource_provider_machines[new_machine_2_CID.hash].get_machine_uuid())

    new_client_1_url = ""
    new_client_1_public_key = 'new_client_1_public_key'
    new_client_1 = Client(new_client_1_public_key, new_client_1_url)
    new_job = Job()
    new_client_1.add_job(new_job)
    # print job requirements
    print(list(new_client_1.get_jobs())[0].get_job_requirements())

    # add client and resource provider to each other's local information
    # new_resource_provider_1.local_information.add_service_provider()
    new_solver_1_public_key = "11"
    new_solver_1_url = "http://solver.com"
    new_solver_1 = Solver(new_solver_1_public_key, new_solver_1_url)

    new_solver_1.local_information.add_service_provider(ServiceType.RESOURCE_PROVIDER,
                                                        new_resource_provider_1_public_key, new_resource_provider_1)
    # should print public key of first resource provider
    print(list(new_solver_1.local_information.get_list_of_service_providers(ServiceType.RESOURCE_PROVIDER).values())[0].get_public_key())

    new_solver_1.local_information.add_service_provider(ServiceType.CLIENT,
                                                        new_client_1_public_key, new_client_1)
    # should print public key of first client
    print(list(new_solver_1.local_information.get_list_of_service_providers(ServiceType.CLIENT).values())[0].get_public_key())

    new_resource_offer_1 = ResourceOffer()
    new_resource_offer_1.add_data('CPU', '6')
    new_resource_offer_1.add_data('RAM', '3')
    new_resource_offer_1.add_data('owner', new_resource_provider_1_public_key)
    new_resource_offer_1.set_id()
    new_resource_offer_1_id = new_resource_offer_1.get_id()
    print(new_resource_offer_1.get_id())

    new_job_offer_1 = JobOffer()
    new_job_offer_1.add_data('CPU', '6')
    new_job_offer_1.add_data('RAM', '3')
    new_job_offer_1.add_data('owner', new_client_1_public_key)
    new_job_offer_1.set_id()
    new_job_offer_1_id = new_job_offer_1.get_id()
    print(new_job_offer_1.get_id())

    new_solver_1.local_information.add_resource_offer(new_resource_offer_1_id, new_resource_offer_1)
    new_solver_1.local_information.add_job_offer(new_job_offer_1_id, new_job_offer_1)

    print(new_solver_1.local_information.get_resource_offers()[new_resource_offer_1_id].get_data().items())
    print(new_solver_1.local_information.get_job_offers()[new_job_offer_1_id].get_data().items())

    new_solver_1.solve()
    # new_match_1 = new_solver_1.match_job_offer(new_job_offer_1)
    # print(new_match_1)

    # new_match_1 = new_solver_1.create_match(new_job_offer_1, new_resource_offer_1)
    # new_match_1.set_id()
    new_match_1 = new_solver_1.get_events()[0].get_data()
    print(new_match_1.get_data())
    print(new_match_1.get_id())

    # new_solver_1.emit_event(new_match_1)
    match_events_1 = new_solver_1.get_events()
    print(match_events_1[0].get_data().get_data())

    # new_solver_1.subscribe_deal(new_resource_provider_1.handler_filter_by_owner_public_key(new_resource_provider_1_public_key), new_match_1)



if __name__ == "__main__":
    main()

