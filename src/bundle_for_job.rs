use alloy::primitives::{Address, U256};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::shared::BundlePrice;
use crate::apiary::bundle_for_job;

#[tokio::main]
#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld Bundle".into())
}

#[tokio::main]
#[pyfunction]
async fn make_buy_statement(
    erc20_addresses_list: Vec<String>,
    erc20_amounts_list: Vec<u64>,
    query: String,
    private_key: String,
) -> PyResult<String> {

    if erc20_addresses_list.len() != erc20_amounts_list.len() {
        return Err(PyValueError::new_err("erc20_addresses_list and erc20_amounts_list must have the same length"));
    }

    let erc20_addresses = erc20_addresses_list.iter().map(|token| {Address::parse_checksummed(token, None).map_err(|_| PyValueError::new_err("couldn't parse token as an address"))}).collect::<Result<Vec<Address>, _>>()?;
    let erc20_amounts: Vec<U256> = erc20_amounts_list.iter().map(|&amount| U256::from(amount)).collect();

    let price = BundlePrice {
        erc20_addresses: erc20_addresses,
        erc20_amounts,
    };

    bundle_for_job::make_buy_statement(price, query, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_bundle_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let bundle_module = PyModule::new_bound(py, "bundle")?;

    bundle_module.add_function(wrap_pyfunction!(helloworld, &bundle_module)?)?;
    bundle_module.add_function(wrap_pyfunction!(make_buy_statement, &bundle_module)?)?;

    parent_module.add_submodule(&bundle_module)?;
    Ok(())
}
