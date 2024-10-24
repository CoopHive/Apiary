use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::standalone::erc20_for_job;

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
    erc20_for_job::make_buy_statement(token, amount, query, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

#[tokio::main]
#[pyfunction]
async fn get_buy_statement(
    statement_uid: String,
    private_key: String,
) -> PyResult<(String, u64, String, String)> {
    erc20_for_job::get_buy_statement(statement_uid, private_key)
        .await
        .map_err(PyErr::from)
        .map(|r| -> PyResult<_> {
            Ok((
                r.token.to_string(),
                r.amount
                    .try_into()
                    .map_err(|_| PyValueError::new_err("amount too big for u64"))?,
                r.arbiter.to_string(),
                r.demand.result, // actually query, unified by abi
            ))
        })?
}

#[tokio::main]
#[pyfunction]
async fn submit_and_collect(
    buy_attestation_uid: String,
    result_cid: String,
    private_key: String,
) -> PyResult<String> {
    erc20_for_job::submit_and_collect(buy_attestation_uid, result_cid, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_erc20_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc20_module = PyModule::new_bound(py, "erc20")?;

    erc20_module.add_function(wrap_pyfunction!(helloworld, &erc20_module)?)?;
    erc20_module.add_function(wrap_pyfunction!(make_buy_statement, &erc20_module)?)?;
    erc20_module.add_function(wrap_pyfunction!(get_buy_statement, &erc20_module)?)?;
    erc20_module.add_function(wrap_pyfunction!(submit_and_collect, &erc20_module)?)?;

    parent_module.add_submodule(&erc20_module)?;
    Ok(())
}
