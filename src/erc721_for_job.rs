use alloy::primitives::{Address, FixedBytes, U256};
use pyo3::{exceptions::PyValueError, prelude::*};

use crate::{shared::ERC721Price, apiary::erc721_for_job};

#[tokio::main]
#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld ERC721".into())
}

#[tokio::main]
#[pyfunction]
async fn make_buy_statement(
    token: String,
    token_id: u64,
    job_cid: String,
    job_input_cid: String,
    private_key: String,
) -> PyResult<String> {
    let price = ERC721Price {
        token: Address::parse_checksummed(&token, None)
            .map_err(|_| PyValueError::new_err("couldn't parse token as an address"))?,
        id: U256::from(token_id),
    };

    erc721_for_job::make_buy_statement(price, job_cid, job_input_cid, private_key)
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

    erc721_for_job::submit_and_collect(buy_attestation_uid, result_cid, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_erc721_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc721_module = PyModule::new_bound(py, "erc721")?;

    erc721_module.add_function(wrap_pyfunction!(helloworld, &erc721_module)?)?;
    erc721_module.add_function(wrap_pyfunction!(make_buy_statement, &erc721_module)?)?;
    erc721_module.add_function(wrap_pyfunction!(submit_and_collect, &erc721_module)?)?;

    parent_module.add_submodule(&erc721_module)?;
    Ok(())
}
