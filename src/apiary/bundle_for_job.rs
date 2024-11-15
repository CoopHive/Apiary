use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes},
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::{
    contracts::{BundlePaymentObligation, JobResultObligation, IEAS, IERC20, IERC721},
    shared::BundlePrice,
};

pub async fn make_buy_statement(
    price: BundlePrice,
    query: String,
    private_key: String,
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let payment_address =
        env::var("BUNDLE_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter_address =
        env::var("TRIVIAL_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData { result: query }
        .abi_encode()
        .into();

    // Iterate over erc20_addresses and erc20_amounts together
    for (erc_20_address, amount) in price.erc20_addresses.iter().zip(price.erc20_amounts.iter()){
        println!("Approving erc_20 tranfer. Address and Amount:");
        println!("{}", erc_20_address);
        println!("{}", amount);
        let token_contract = IERC20::new(*erc_20_address, &provider);

        let mut call = token_contract
        .approve(payment_address, *amount);
        
        // let gas_estimate = call
        // .estimate_gas()
        // .await?;
        // println!("Gas estimated");
        // let gas_limit = gas_estimate * 120 / 100;
        let gas_limit = 2_000_000u128;
        call = call.gas(gas_limit);
        // println!("Gas limit set");

        let approval_receipt = call
        .send()
        .await?
        .get_receipt()
        .await?;

        if !approval_receipt.status() {
            return Err(eyre::eyre!("approval failed"));
        };
    }

    // Iterate over erc721_addresses and erc721_ids together
    for (erc_721_address, id) in price.erc721_addresses.iter().zip(price.erc721_ids.iter()){
        let token_contract = IERC721::new(*erc_721_address, &provider);

        let mut call = token_contract
        .approve(payment_address, *id);

        let approval_receipt = call
        .send()
        .await?
        .get_receipt()
        .await?;

        if !approval_receipt.status() {
            return Err(eyre::eyre!("approval failed"));
        };
    }

    let statement_contract = BundlePaymentObligation::new(payment_address, &provider);

    let mut call = statement_contract
    .makeStatement(
        BundlePaymentObligation::StatementData {
            erc20Addresses: price.erc20_addresses,
            erc20Amounts: price.erc20_amounts,
            erc721Addresses: price.erc721_addresses,
            erc721Ids: price.erc721_ids,
            arbiter: arbiter_address,
            demand,
        },
        0,
        b256!("0000000000000000000000000000000000000000000000000000000000000000"),
    );

    // let gas_estimate = call
    // .estimate_gas()
    // .await?;
    // println!("Gas estimated");
    // let gas_limit = gas_estimate * 120 / 100;
    let gas_limit = 5_000_000u128;
    call = call.gas(gas_limit);

    let log = call
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
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attested"))??;

    Ok(log.inner.uid)
}

pub struct JobPayment {
    pub price: BundlePrice,
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
        env::var("BUNDLE_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let result_contract = JobResultObligation::new(result_address, &provider);
    let payment_contract = BundlePaymentObligation::new(payment_address, &provider);

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
