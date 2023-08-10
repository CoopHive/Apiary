"""
Test entrypoint script.
"""

from contract import Contract, ServiceType, Tx, CID
import pprint
import random
from machine import Machine
from resource_provider import ResourcePovider
from client import Client
from job import Job

class Address:
    def __init__(self):
        self.current_address = 0

    def get_current_address(self):
        return self.current_address

    def increment_current_address(self):
        self.current_address += 1

def main():
    contract = Contract()

    address = Address()

    def create_new_address():
        if len(contract.wallets) != 0:
            Address.increment_current_address(address)
        return hex(Address.get_current_address(address))
        # return Address.get_current_address(address)

    for _ in range(2):
        contract.register_service_provider(
            ServiceType.SOLVER,
            "http://foo1.com",
            {"labels": ["local-test"]},
            Tx(create_new_address(), 0)
        )

        contract.register_service_provider(
            ServiceType.DIRECTORY,
            "http://foo2.com",
            {"labels": ["local-test"]},
            Tx(create_new_address(), 0)
        )

        contract.register_service_provider(
            ServiceType.CLIENT,
            "",
            {"labels": ["local-test"]},
            Tx(create_new_address(), 0)
        )

        contract.register_service_provider(
            ServiceType.RESOURCE_PROVIDER,
            "",
            {"labels": ["local-test"]},
            Tx(create_new_address(), 0)
        )

        contract.register_service_provider(
            ServiceType.MEDIATOR,
            "",
            {"labels": ["local-test"]},
            Tx(create_new_address(), 0)
        )



    def get_list_of_service_providers(service_type: ServiceType):
        match service_type:
            case ServiceType.RESOURCE_PROVIDER:
                return contract.resource_providers
            case ServiceType.CLIENT:
                return contract.clients
            case ServiceType.SOLVER:
                return contract.solvers
            case ServiceType.MEDIATOR:
                return contract.mediators
            case ServiceType.DIRECTORY:
                return contract.directories

    print("--> block_number")
    pprint.pprint(contract.block_number) 
    print("--> wallets")
    pprint.pprint(contract.wallets)

    print("--> resource_providers")
    pprint.pprint(get_list_of_service_providers(ServiceType.RESOURCE_PROVIDER))
    print("--> clients")
    pprint.pprint(get_list_of_service_providers(ServiceType.CLIENT))
    print("--> solvers")
    pprint.pprint(get_list_of_service_providers(ServiceType.SOLVER))
    print("--> directories")
    pprint.pprint(get_list_of_service_providers(ServiceType.DIRECTORY))
    print("--> mediators")
    pprint.pprint(get_list_of_service_providers(ServiceType.MEDIATOR))

    mediators = get_list_of_service_providers(ServiceType.MEDIATOR)
    some_mediator_address = random.choice(list(mediators.keys()))
    print(f'mediator being removed: {some_mediator_address}')
    contract.unregister_service_provider(
        ServiceType.MEDIATOR,
        Tx(some_mediator_address, 0))

    print("--> mediators after removing mediator")
    pprint.pprint(get_list_of_service_providers(ServiceType.MEDIATOR))

    machine_attributes = {'CPU', 'RAM'}
    new_machine_1 = Machine(machine_attributes)
    new_machine_1.add_data('CPU', '4')
    new_machine_1.add_data('RAM', '2')
    # should throw exception if GPU is not one of the machine attributes
    # new_machine_1.add_data('GPU', '3090')
    machine_data = new_machine_1.get_machine_data()
    print(machine_data)

    new_machine_2 = Machine(machine_attributes)
    new_machine_2.add_data('CPU', '8')
    new_machine_2.add_data('RAM', '4')


    new_resource_provider = ResourcePovider('0')
    new_machine_1_CID = CID('1', {})
    new_machine_2_CID = CID('2', {})
    new_resource_provider.add_machine(new_machine_1_CID, new_machine_1)
    new_resource_provider.add_machine(new_machine_2_CID, new_machine_2)
    resource_provider_machines = new_resource_provider.get_machines()
    print(resource_provider_machines)
    # should match above
    print(resource_provider_machines[new_machine_1_CID.hash].get_machine_data())
    print(resource_provider_machines[new_machine_2_CID.hash].get_machine_data())

    print(resource_provider_machines[new_machine_1_CID.hash].get_machine_uuid())
    print(resource_provider_machines[new_machine_2_CID.hash].get_machine_uuid())

    new_client = Client('1')
    new_job = Job()
    new_client.add_job(new_job)
    # print job requirements
    print(list(new_client.get_jobs())[0].get_job_requirements())

    # # add client and resource provider to each others's local information
    # new_resource_provider.local_information.add_service_provider()



if __name__ == "__main__":
    main()
