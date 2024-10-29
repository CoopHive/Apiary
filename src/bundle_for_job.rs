use alloy::primitives::{Address, FixedBytes, U256};
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
    erc721_addresses_list: Vec<String>,
    erc721_ids_list: Vec<u64>,
    query: String,
    private_key: String,
) -> PyResult<String> {

    if erc20_addresses_list.len() != erc20_amounts_list.len() {
        return Err(PyValueError::new_err("erc20_addresses_list and erc20_amounts_list must have the same length"));
    }
    if erc721_addresses_list.len() != erc721_ids_list.len() {
        return Err(PyValueError::new_err("erc721_addresses_list and erc721_ids_list must have the same length"));
    }

    let erc20_addresses = erc20_addresses_list.iter().map(|token| {Address::parse_checksummed(token, None).map_err(|_| PyValueError::new_err("couldn't parse token as an address"))}).collect::<Result<Vec<Address>, _>>()?;
    let erc20_amounts: Vec<alloy::primitives::Uint<256, 4>> = erc20_amounts_list.iter().map(|&amount| U256::from(amount)).collect();

    let erc721_addresses = erc721_addresses_list.iter().map(|token| {Address::parse_checksummed(token, None).map_err(|_| PyValueError::new_err("couldn't parse token as an address"))}).collect::<Result<Vec<Address>, _>>()?;
    let erc721_ids: Vec<alloy::primitives::Uint<256, 4>> = erc721_ids_list.iter().map(|&id| U256::from(id)).collect();

    let price = BundlePrice {
        erc20_addresses: erc20_addresses,
        erc20_amounts: erc20_amounts,
        erc721_addresses: erc721_addresses,
        erc721_ids: erc721_ids
    };

    bundle_for_job::make_buy_statement(price, query, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

#[tokio::main]
#[pyfunction]
async fn get_buy_statement(
    statement_uid: String,
) -> PyResult<(Vec<String>, Vec<u64>, Vec<String>, Vec<u64>, String, String)> {
    let statement_uid: FixedBytes<32> = statement_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| PyValueError::new_err("couldn't parse statement_uid as bytes32"))?;

    bundle_for_job::get_buy_statement(statement_uid)
        .await
        .map_err(PyErr::from)
        .map(|r| -> PyResult<_> {
            Ok((
                r.price.erc20_addresses
                .iter()
                .map(|address| address.to_string())
                .collect::<Vec<String>>(),

                r.price.erc20_amounts
                    .iter()
                    .map(|amount| {
                        <&alloy::primitives::Uint<256, 4> as TryInto<u64>>::try_into(amount)
                        .map_err(|_| PyValueError::new_err("amount too big for u64"))
                })
                .collect::<Result<Vec<u64>, _>>()?,

                r.price.erc721_addresses
                .iter()
                .map(|address| address.to_string())
                .collect::<Vec<String>>(),

                r.price.erc721_ids
                    .iter()
                    .map(|amount| {
                        <&alloy::primitives::Uint<256, 4> as TryInto<u64>>::try_into(amount)
                        .map_err(|_| PyValueError::new_err("amount too big for u64"))
                })
                .collect::<Result<Vec<u64>, _>>()?,

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
    let buy_attestation_uid: FixedBytes<32> = buy_attestation_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| PyValueError::new_err("couldn't parse buy_attestation_uid as bytes32"))?;

        bundle_for_job::submit_and_collect(buy_attestation_uid, result_cid, private_key)
        .await
        .map(|x| x.to_string())
        .map_err(PyErr::from)
}

pub fn add_bundle_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let bundle_module = PyModule::new_bound(py, "bundle")?;

    bundle_module.add_function(wrap_pyfunction!(helloworld, &bundle_module)?)?;
    bundle_module.add_function(wrap_pyfunction!(make_buy_statement, &bundle_module)?)?;
    bundle_module.add_function(wrap_pyfunction!(get_buy_statement, &bundle_module)?)?;
    bundle_module.add_function(wrap_pyfunction!(submit_and_collect, &bundle_module)?)?;

    parent_module.add_submodule(&bundle_module)?;
    Ok(())
}
