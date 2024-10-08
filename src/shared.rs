use alloy::{
    primitives::{Address, FixedBytes},
    sol,
    sol_types::SolValue,
};
use pyo3::{
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
};
use std::env;

use crate::provider;


pub fn py_val_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyValueError, _>(msg.into())
}

pub fn py_run_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyRuntimeError, _>(msg.into())
}

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    JobResultObligation,
    "src/contracts/JobResultObligation.json"
);


sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IEAS,
    "src/contracts/IEAS.json"
);

#[tokio::main]
#[pyfunction]
pub async fn get_result_cid_from_sell_uid(sell_uid: String, private_key: String) -> PyResult<String> {
    let provider = provider::get_provider(private_key)?;

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
