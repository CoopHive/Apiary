use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes},
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::{
    contracts::{ERC20PaymentObligation, JobResultObligation, IEAS, IERC20},
    shared::ERC20Price,
};

pub async fn make_buy_statement(
    price: ERC20Price,
    query: String,
    private_key: String,
) -> eyre::Result<(FixedBytes<32>, u128)> {
    let provider = provider::get_wallet_provider(private_key)?;

    // let gas_price = provider.get_gas_price().await?;
    let mut gas_used: u128 = 0;

    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter_address =
        env::var("TRIVIAL_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData { result: query }
        .abi_encode()
        .into();

     // Approve the payment
    let token_contract = IERC20::new(price.token, &provider);
    let mut approval_call = token_contract.approve(payment_address, price.amount);

    let gas_limit = 2_000_000u128;
    approval_call = approval_call.gas(gas_limit);

    let approval_receipt = approval_call
        .send()
        .await?
        .get_receipt()
        .await?;

    if !approval_receipt.status() {
        return Err(eyre::eyre!("approval failed"));
    };

    gas_used = gas_used + approval_receipt.gas_used;

    // Make the statement
    let statement_contract = ERC20PaymentObligation::new(payment_address, &provider);
    let mut statement_call = statement_contract.makeStatement(
        ERC20PaymentObligation::StatementData {
            token: price.token,
            amount: price.amount,
            arbiter: arbiter_address,
            demand,
        },
        0,
        b256!("0000000000000000000000000000000000000000000000000000000000000000"),
    );

    let gas_limit = 5_000_000u128;
    statement_call = statement_call.gas(gas_limit);

    let statement_receipt = statement_call
        .send()
        .await?
        .get_receipt()
        .await?;

    gas_used = gas_used + statement_receipt.gas_used;

    let log = statement_receipt
        .inner
        .logs()
        .iter()
        .filter(|log| log.topic0() == Some(&IEAS::Attested::SIGNATURE_HASH))
        .collect::<Vec<_>>()
        .first()
        .map(|log| log.log_decode::<IEAS::Attested>())
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attested"))??;

    Ok((log.inner.uid, gas_used))
}

pub struct JobPayment {
    pub price: ERC20Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub async fn submit_and_collect(
    buy_attestation_uid: FixedBytes<32>,
    result_cid: String,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let result_address =
        env::var("JOB_RESULT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let result_contract = JobResultObligation::new(result_address, &provider);
    let payment_contract = ERC20PaymentObligation::new(payment_address, &provider);

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
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attested"))??;

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
