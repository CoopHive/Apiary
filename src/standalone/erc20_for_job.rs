use alloy::{
    primitives::{b256, Address, Bytes, FixedBytes, U256},
    sol,
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::provider;
use crate::shared::{JobResultObligation, IEAS};

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC20PaymentObligation,
    "src/contracts/ERC20PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC20,
    "src/contracts/IERC20.json"
);

pub async fn make_buy_statement(
    token: String,
    amount: u64,
    query: String,
    private_key: String,
) -> eyre::Result<String> {
    let provider = provider::get_provider(private_key)?;

    let token_address = Address::parse_checksummed(&token, None)?;
    let amount = U256::from(amount);
    let arbiter = env::var("TRIVIAL_ARBITER").map(|a| Address::parse_checksummed(a, None))??;
    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData { result: query }
        .abi_encode()
        .into();

    let payment_address =
        env::var("ERC20_PAYMENT_OBLIGATION").map(|a| Address::parse_checksummed(a, None))??;

    let token_contract = IERC20::new(token_address, &provider);
    let statement_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, amount)
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
                token: token_address,
                amount,
                arbiter,
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

    Ok(log.inner.uid.to_string())
}

pub async fn get_buy_statement(
    statement_uid: String,
    private_key: String,
) -> eyre::Result<(String, u64, String, String)> {
    let provider = provider::get_provider(private_key)?;
    let statement_uid: FixedBytes<32> = statement_uid.parse::<FixedBytes<32>>()?;
    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;
    let contract = IEAS::new(eas_address, provider);
    let attestation = contract.getAttestation(statement_uid).call().await?._0;

    let attestation_data =
        ERC20PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

    let (token, amount, arbiter, demand) = (
        attestation_data.token,
        attestation_data.amount,
        attestation_data.arbiter,
        attestation_data.demand,
    );
    let amount: u64 = amount.try_into()?;
    let demand = JobResultObligation::StatementData::abi_decode(&demand, true)?;

    Ok((
        token.to_string(),
        amount,
        arbiter.to_string(),
        demand.result,
    ))
}

pub async fn submit_and_collect(
    buy_attestation_uid: String,
    result_cid: String,
    private_key: String,
) -> eyre::Result<String> {
    let provider = provider::get_provider(private_key)?;

    let buy_attestation_uid = buy_attestation_uid.parse::<FixedBytes<32>>()?;

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
        Ok(sell_uid.to_string())
    } else {
        Err(eyre::eyre!("contract call to collect payment failed"))
    }
}
