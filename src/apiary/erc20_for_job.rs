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
) -> eyre::Result<FixedBytes<32>> {
    let provider = provider::get_wallet_provider(private_key)?;

    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;
    let arbiter_address =
        env::var("TRIVIAL_ARBITER").map(|a| Address::parse_checksummed(a, None))??;

    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData { result: query }
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
        .ok_or_else(|| eyre::eyre!("makeStatement logs didn't contain Attested"))??;

    Ok(log.inner.uid)
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

#[cfg(test)]
mod tests {
    use alloy::primitives::address;

    use super::*;

    #[tokio::test]
    async fn test_make_buy_job() {
        let price = ERC20Price {
            token: address!("833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
            amount: 1000.try_into().unwrap(),
        };
        let buyer_privkey = env::var("PRIVKEY_BUYER").unwrap();

        let statement_uid = make_buy_statement(price, "hello".to_string(), buyer_privkey)
            .await
            .unwrap();

        println!("statement_uid: {:?}", statement_uid);
    }
}
