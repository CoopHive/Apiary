"""
Test entrypoint script.
"""

from simulator.contract import Contract, ServiceType, Tx
import pprint

def main():
    contract = Contract()

    rp_addr_1 = "0x00001"
    rp_addr_2 = "0x00002"

    contract.register_service_provider(
        ServiceType.RESOURCE_PROVIDER,
        "http://foo.com",
        {"labels": ["local-test"]},
        Tx(rp_addr_1, 0)
    )

    contract.register_service_provider(
        ServiceType.RESOURCE_PROVIDER,
        "http://bar.com",
        {"labels": ["local-test"]},
        Tx(rp_addr_2, 0)
    )

    print("--> block_number")
    pprint.pprint(contract.block_number) 
    print("--> wallets")
    pprint.pprint(contract.wallets) 
    print("--> resource_providers")
    pprint.pprint(contract.resource_providers) 

if __name__ == "__main__":
    main()