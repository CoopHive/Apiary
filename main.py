"""
Test entrypoint script.
"""

from simulator.contract import Contract, ServiceType, Tx
import pprint

def main():
    contract = Contract()

    rp_addr_1 = "0x00001"
    rp_addr_2 = "0x00002"
    jc_addr_1 = "0x00011"

    contract.register_service_provider(
        ServiceType.SOLVER,
        "http://foo1.com",
        {"labels": ["local-test"]},
        Tx(rp_addr_1, 0)
    )

    contract.register_service_provider(
        ServiceType.DIRECTORY,
        "http://foo2.com",
        {"labels": ["local-test"]},
        Tx(rp_addr_2, 0)
    )

    contract.register_service_provider(
        ServiceType.JOB_CREATOR,
        "",
        {"labels": ["local-test"]},
        Tx(jc_addr_1, 0)
    )

    contract.register_service_provider(
        ServiceType.RESOURCE_PROVIDER,
        "",
        {"labels": ["local-test"]},
        Tx(jc_addr_1, 0)
    )


    print("--> block_number")
    pprint.pprint(contract.block_number) 
    print("--> wallets")
    pprint.pprint(contract.wallets) 
    print("--> resource_providers")
    pprint.pprint(contract.resource_providers) 
    print("--> job_creators")
    pprint.pprint(contract.job_creators) 



if __name__ == "__main__":
    main()