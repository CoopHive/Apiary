use alloy::{
    primitives::{b256, Address, Bytes, FixedBytes},
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::{
    contracts::{BundlePaymentObligation, JobResultObligation, IEAS, IERC20},
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
        let token_contract = IERC20::new(*erc_20_address, &provider);

        let approval_receipt = token_contract
        .approve(payment_address, *amount)
        .send()
        .await?
        .get_receipt()
        .await?;

        if !approval_receipt.status() {
            return Err(eyre::eyre!("approval failed"));
        };
    }

    // Iterate over erc721_addresses and erc721_ids together
    // for (erc_721_address, id) in price.erc721_addresses.iter().zip(price.erc721_ids.iter()) {
    // }

    let statement_contract = BundlePaymentObligation::new(payment_address, &provider);

    let log = statement_contract
        .makeStatement(
            BundlePaymentObligation::StatementData {
                erc20Addresses: price.erc20_addresses,
                erc20Amounts: price.erc20_amounts,
                erc721Addresses: vec![],
                erc721Ids: vec![],
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
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attested"))??;

    Ok(log.inner.uid)
}
