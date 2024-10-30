use alloy::{
    primitives::{b256, Address, FixedBytes},
    sol,
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::{
    contracts::{ERC20PaymentObligation, RedisProvisionObligation, IEAS, IERC20},
    shared::ERC20Price,
};

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
    price: ERC20Price,
    demand: RedisProvisionDemand,
    service_provider: Address,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let redis_provision_obligation_address =
        env::var("REDIS_PROVISION_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter_address =
        env::var("TRUSTED_PARTY_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    let base_demand = demand.abi_encode().into();
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

pub struct RedisProvisionPayment {
    pub price: ERC20Price,
    pub arbiter: Address,
    pub base_demand: RedisProvisionDemand,
    pub provider_demand: Address,
}

pub async fn get_buy_statement(
    statement_uid: FixedBytes<32>,
) -> eyre::Result<RedisProvisionPayment> {
    let provider = provider::get_public_provider()?;
    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract.getAttestation(statement_uid).call().await?._0;

    let attestation_data =
        ERC20PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;
    let trusted_party_demand =
        TrustedPartyDemand::abi_decode(attestation_data.demand.as_ref(), true)?;
    let base_demand =
        RedisProvisionDemand::abi_decode(trusted_party_demand.baseDemand.as_ref(), true)?;

    Ok(RedisProvisionPayment {
        price: ERC20Price {
            token: attestation_data.token,
            amount: attestation_data.amount,
        },
        arbiter: attestation_data.arbiter,
        base_demand,
        provider_demand: trusted_party_demand.creator,
    })
}

#[derive(Debug)]
pub struct ProvisionData {
    pub statement_data: RedisProvisionObligation::StatementData,
    pub provider: Address,
    pub expiration: u64,
    pub replaces: Option<FixedBytes<32>>,
}

pub async fn get_sell_statement(statement_uid: FixedBytes<32>) -> eyre::Result<ProvisionData> {
    let provider = provider::get_public_provider()?;
    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);
    let attestation = contract.getAttestation(statement_uid).call().await?._0;

    let attestation_data =
        RedisProvisionObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

    Ok(ProvisionData {
        statement_data: attestation_data,
        provider: attestation.recipient,
        expiration: attestation.expirationTime,
        replaces: if attestation.refUID == FixedBytes::<32>::default() {
            None
        } else {
            Some(attestation.refUID)
        },
    })
}

pub async fn update_and_collect(
    buy_attestation_uid: FixedBytes<32>,
    old_statement_uid: FixedBytes<32>,
    revision: RedisProvisionObligation::StatementData,
    new_expiration: u64,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let result_address =
        env::var("REDIS_PROVISION_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let result_contract = RedisProvisionObligation::new(result_address, &provider);
    let payment_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let sell_uid = result_contract
        .reviseStatement(old_statement_uid, revision, new_expiration)
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
        .map(|log| log.log_decode::<IEAS::Attested>().map(|a| a.inner.uid))
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attest"))??;

    let collect_receipt = payment_contract
        .collectPayment(buy_attestation_uid, sell_uid)
        .send()
        .await?
        .get_receipt()
        .await?;

    if collect_receipt.status() {
        Ok(sell_uid)
    } else {
        Err(eyre::eyre!("contract call to collect payment failed"))
    }
}

pub async fn make_new_and_collect(
    buy_attestation_uid: FixedBytes<32>,
    provision: RedisProvisionObligation::StatementData,
    expiration: u64,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let result_address =
        env::var("REDIS_PROVISION_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let result_contract = RedisProvisionObligation::new(result_address, &provider);
    let payment_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let sell_uid = result_contract
        .makeStatement(
            RedisProvisionObligation::StatementData {
                user: provision.user,
                capacity: provision.capacity,
                egress: provision.egress,
                cpus: provision.cpus,
                serverName: provision.serverName,
                url: provision.url,
            },
            expiration,
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
        .map(|log| log.log_decode::<IEAS::Attested>().map(|a| a.inner.uid))
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attest"))??;

    let collect_receipt = payment_contract
        .collectPayment(buy_attestation_uid, sell_uid)
        .send()
        .await?
        .get_receipt()
        .await?;

    if collect_receipt.status() {
        Ok(sell_uid)
    } else {
        Err(eyre::eyre!("contract call to collect payment failed"))
    }
}

#[cfg(test)]
mod tests {
    use alloy::{primitives::address, signers::local::PrivateKeySigner};

    use super::*;

    #[tokio::test]
    async fn test_make_buy_redis() {
        let price = ERC20Price {
            token: address!("833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
            amount: 1000.try_into().unwrap(),
        };
        let buyer_privkey = env::var("PRIVKEY_BUYER").unwrap();
        let buyer: PrivateKeySigner = buyer_privkey.parse().unwrap();
        let seller: PrivateKeySigner = env::var("PRIVKEY_SELLER").unwrap().parse().unwrap();

        let demand = RedisProvisionDemand {
            replaces: FixedBytes::<32>::default(),
            user: buyer.address(),
            capacity: 1000.try_into().unwrap(),
            egress: 1000.try_into().unwrap(),
            cpus: 1.try_into().unwrap(),
            expiration: 1679808000,
            serverName: "redis-server".to_string(),
        };
        let service_provider = seller.address();

        let statement_uid = make_buy_statement(price, demand, service_provider, buyer_privkey)
            .await
            .unwrap();

        println!("statement_uid: {:?}", statement_uid);
    }
}
