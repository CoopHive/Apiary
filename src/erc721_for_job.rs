use alloy::sol;
use pyo3::{exceptions::PyValueError, prelude::*};

use crate::standalone::erc721_for_job;

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC721PaymentObligation,
    "src/contracts/ERC721PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC721,
    "src/contracts/IERC721.json"
);

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
    query: String,
    private_key: String,
) -> PyResult<String> {
    erc721_for_job::make_buy_statement(token, token_id, query, private_key)
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
    erc721_for_job::get_buy_statement(statement_uid, private_key)
        .await
        .map(|r| -> PyResult<_> {
            Ok((
                r.token.to_string(),
                r.token_id
                    .try_into()
                    .map_err(|_| PyValueError::new_err("token_id too big for u64"))?,
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
    erc721_for_job::submit_and_collect(buy_attestation_uid, result_cid, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_erc721_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc721_module = PyModule::new_bound(py, "erc721")?;

    erc721_module.add_function(wrap_pyfunction!(helloworld, &erc721_module)?)?;
    erc721_module.add_function(wrap_pyfunction!(make_buy_statement, &erc721_module)?)?;
    erc721_module.add_function(wrap_pyfunction!(get_buy_statement, &erc721_module)?)?;
    erc721_module.add_function(wrap_pyfunction!(submit_and_collect, &erc721_module)?)?;

    parent_module.add_submodule(&erc721_module)?;
    Ok(())
}
