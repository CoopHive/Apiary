use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes},
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::{
    contracts::{ERC721PaymentObligation, JobResultObligation, IEAS, IERC721},
    shared::ERC721Price,
};

pub async fn make_buy_statement(
    price: ERC721Price,
    query: String,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_provider(private_key)?;

    let arbiter_address =
        env::var("TRIVIAL_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData { result: query }
        .abi_encode()
        .into();

    let payment_address =
        env::var("ERC721_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let token_contract = IERC721::new(price.token, &provider);
    let statement_contract = ERC721PaymentObligation::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, price.id)
        .send()
        .await?
        .get_receipt()
        .await?;

    if !approval_receipt.status() {
        return Err(eyre::eyre!("approval failed"));
    };

    let log = statement_contract
        .makeStatement(
            ERC721PaymentObligation::StatementData {
                token: price.token,
                tokenId: price.id,
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

pub struct JobPayment {
    pub price: ERC721Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub async fn get_buy_statement(
    statement_uid: FixedBytes<32>,
    private_key: String,
) -> eyre::Result<JobPayment> {
    let provider = provider::get_provider(private_key)?;
    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract.getAttestation(statement_uid).call().await?._0;

    let attestation_data =
        ERC721PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

    Ok(JobPayment {
        price: ERC721Price {
            token: attestation_data.token,
            id: attestation_data.tokenId,
        },
        arbiter: attestation_data.arbiter,
        demand: JobResultObligation::StatementData::abi_decode(&attestation_data.demand, true)?,
    })
}

pub async fn submit_and_collect(
    buy_attestation_uid: FixedBytes<32>,
    result_cid: String,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_provider(private_key)?;
    let result_address =
        env::var("JOB_RESULT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let payment_address =
        env::var("ERC721_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let result_contract = JobResultObligation::new(result_address, &provider);
    let payment_contract = ERC721PaymentObligation::new(payment_address, &provider);

    let sell_uid = result_contract
        .makeStatement(
            JobResultObligation::StatementData { result: result_cid },
            buy_attestation_uid,
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
