use alloy::primitives::{Address, FixedBytes, U256};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::shared::ERC20Price;
use crate::apiary::erc20_for_job;

#[tokio::main]
#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld ERC20".into())
}

#[tokio::main]
#[pyfunction]
async fn make_buy_statement(
    token: String,
    amount: u64,
    query: String,
    private_key: String,
) -> PyResult<String> {
    let price = ERC20Price {
        token: Address::parse_checksummed(&token, None)
            .map_err(|_| PyValueError::new_err("couldn't parse token as an address"))?,
        amount: U256::from(amount),
    };

    erc20_for_job::make_buy_statement(price, query, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

#[tokio::main]
#[pyfunction]
async fn submit_and_collect(
    buy_attestation_uid: String,
    result_cid: String,
    private_key: String,
) -> PyResult<String> {
    let buy_attestation_uid: FixedBytes<32> = buy_attestation_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| PyValueError::new_err("couldn't parse buy_attestation_uid as bytes32"))?;

    erc20_for_job::submit_and_collect(buy_attestation_uid, result_cid, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_erc20_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc20_module = PyModule::new_bound(py, "erc20")?;

    erc20_module.add_function(wrap_pyfunction!(helloworld, &erc20_module)?)?;
    erc20_module.add_function(wrap_pyfunction!(make_buy_statement, &erc20_module)?)?;
    erc20_module.add_function(wrap_pyfunction!(submit_and_collect, &erc20_module)?)?;

    parent_module.add_submodule(&erc20_module)?;
    Ok(())
}
