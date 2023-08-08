"""
Test entrypoint script.
"""

from simulator.contract import Contract, ServiceType, Tx
import pprint

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
            ServiceType.JOB_CREATOR,
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
            case ServiceType.JOB_CREATOR:
                return contract.job_creators
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
    print("--> job_creators")
    pprint.pprint(get_list_of_service_providers(ServiceType.JOB_CREATOR))
    print("--> solvers")
    pprint.pprint(get_list_of_service_providers(ServiceType.SOLVER))
    print("--> directories")
    pprint.pprint(get_list_of_service_providers(ServiceType.DIRECTORY))
    print("--> mediators")
    pprint.pprint(get_list_of_service_providers(ServiceType.MEDIATOR))




if __name__ == "__main__":
    main()