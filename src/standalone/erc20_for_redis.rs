use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes, U256},
    sol,
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::contracts::{ERC20PaymentObligation, RedisProvisionObligation, IEAS, IERC20};
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

    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let redis_provision_obligation_address =
        env::var("REDIS_PROVISION_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter_address =
        env::var("TRUSTED_PARTY_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    let base_demand: Bytes = demand.abi_encode().into();
    let demand = TrustedPartyDemand {
        creator: service_provider,
        baseArbiter: redis_provision_obligation_address,
        baseDemand: base_demand,
    }
    .abi_encode()
    .into();

    let token_contract = IERC20::new(price.token, &provider);
    let statement_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, price.amount)
        .send()
        .await?
        .get_receipt()
        .await?;

    if !approval_receipt.status() {
        return Err(eyre::eyre!("approval failed"));
    };

    let log = statement_contract
        .makeStatement(
            ERC20PaymentObligation::StatementData {
                token: price.token,
                amount: price.amount,
                arbiter: arbiter_address,
                demand,
            },
            0,
            b256!("0000000000000000000000000000000000000000000000000000000000000000"),
        )
        .send()
        .await?
        .get_receipt()
        .await?
        .inner
        .logs()
        .iter()
        .filter(|log| log.topic0() == Some(&IEAS::Attested::SIGNATURE_HASH))
        .collect::<Vec<_>>()
        .first()
        .map(|log| log.log_decode::<IEAS::Attested>())
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attest"))??;

    Ok(log.inner.uid)
}
