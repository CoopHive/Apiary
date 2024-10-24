use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes, U256},
    sol,
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::contracts::{
    ERC20PaymentObligation, RedisProvisionObligation, TrustedPartyArbiter, IEAS, IERC20,
};
use crate::provider;

sol! {
    #[allow(missing_docs)]
    #[derive(Debug)]
    /// RedisProvisionDemand
    struct RedisProvisionDemand {
        bytes32 replaces;
        address user;
        uint256 capacity;
        uint256 egress;
        uint256 cpus;
        uint64 expiration;
        string serverName;
    }

    #[allow(missing_docs)]
    #[derive(Debug)]
    /// TrustedPartyDemand
    struct TrustedPartyDemand {
        address creator;
        address baseArbiter;
        bytes baseDemand;
    }
}

pub async fn make_buy_statement(
    price: ERC20PaymentObligation::StatementData,
    demand: RedisProvisionDemand,
    service_provider: Address,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_provider(private_key)?;

    let redis_provision_obligation_address =
        env::var("REDIS_PROVISION_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter =
        env::var("TRUSTED_PARTY_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    let base_demand: Bytes = demand.abi_encode().into();
    let demand = TrustedPartyDemand {
        creator: service_provider,
        baseArbiter: redis_provision_obligation_address,
        baseDemand: base_demand,
    };

    Ok(FixedBytes::<32>::default())
}
