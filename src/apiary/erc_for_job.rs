use pyo3::prelude::*;
use crate::provider;
use std::env;

use alloy::{
    primitives::{self, Address, FixedBytes},
    sol_types::SolValue,
};

use crate::shared::{py_val_err, py_run_err, ERC20Price, ERC721Price, BundlePrice};
use crate::contracts::{ERC20PaymentObligation, JobResultObligation, IEAS};

pub struct JobPayment20 {
    pub price: ERC20Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub struct JobPayment721 {
    pub price: ERC721Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub struct JobPaymentBundle {
    pub price: BundlePrice,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub enum JobPaymentResult {
    JobPayment20(JobPayment20),
    JobPayment721(JobPayment721),
    JobPaymentBundle(JobPaymentBundle),
}

pub async fn get_buy_statement(
    statement_uid: FixedBytes<32>,
) -> eyre::Result<JobPaymentResult> {
    let provider = provider::get_public_provider()?;

    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);
    let attestation = contract.getAttestation(statement_uid).call().await?._0;
    
    // Use right statement_data based on attestation.schema
    let attestation_data =
        ERC20PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

    // Use right JobPaymentResult based on attestation.schema
    Ok(JobPaymentResult::JobPayment20(JobPayment20 {
        price: ERC20Price {
            token: attestation_data.token,
            amount: attestation_data.amount,
        },
        arbiter: attestation_data.arbiter,
        demand: JobResultObligation::StatementData::abi_decode(&attestation_data.demand, true)?,
    }))
}

// GENERALIZE THIS INTO GET_SELL_STATEMENT, same API as get_buy_statement
#[tokio::main]
#[pyfunction]
pub async fn get_result_cid_from_sell_uid(
    sell_uid: String,
) -> PyResult<String> {
    let provider = provider::get_public_provider()?;

    let sell_uid = sell_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| py_val_err("couldn't parse sell_uid as bytes32"))?;

    let eas_address = env::var("EAS_CONTRACT")
        .map_err(|_| py_val_err("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse EAS_CONTRACT as an address"))?;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract
        .getAttestation(sell_uid)
        .call()
        .await
        .map_err(|err| py_run_err(format!("contract call to getAttestation failed; {:?}", err)))?
        ._0;

    let attestation_data =
        JobResultObligation::StatementData::abi_decode(attestation.data.as_ref(), true)
            .map_err(|_| py_run_err("attestation_data decoding failed"))?;

    Ok(attestation_data.result)
}
