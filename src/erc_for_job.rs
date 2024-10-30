use alloy::primitives::FixedBytes;
use pyo3::exceptions::PyValueError;

use pyo3::prelude::*;
use crate::apiary::erc_for_job;
use crate::apiary::erc_for_job::JobPaymentResult;

#[tokio::main]
#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld ERC".into())
}

#[pyclass]
pub enum BuyStatement {
    Single(String, u64, String, String),
    Multiple(Vec<String>, Vec<u64>, Vec<String>, Vec<u64>, String, String),
}

#[tokio::main]
#[pyfunction]
async fn get_buy_statement(
    statement_uid: String,
) -> PyResult<BuyStatement> {
    let statement_uid: FixedBytes<32> = statement_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| PyValueError::new_err("couldn't parse statement_uid as bytes32"))?;

    let payment_result = erc_for_job::get_buy_statement(statement_uid)
        .await
        .map_err(PyErr::from)?;

    match payment_result {
        JobPaymentResult::JobPayment20(payment) => {
            let result = BuyStatement::Single(
                payment.price.token.to_string(),
                payment.price.amount.try_into()
                    .map_err(|_| PyValueError::new_err("amount too big for u64"))?,
                payment.arbiter.to_string(),
                payment.demand.result.to_string(),
            );
            Ok(result)
        },
        JobPaymentResult::JobPayment721(payment) => {
            let result = BuyStatement::Single(
                payment.price.token.to_string(),
                payment.price.id.try_into()
                    .map_err(|_| PyValueError::new_err("amount too big for u64"))?,
                payment.arbiter.to_string(),
                payment.demand.result.to_string(),
            );
            Ok(result)
        },
        JobPaymentResult::JobPaymentBundle(payment) => {
            let result = BuyStatement::Multiple(
                payment.price.erc20_addresses.iter()
                .map(|address| address.to_string())
                .collect::<Vec<String>>(),

                payment.price.erc20_amounts
                .iter()
                .map(|amount| {
                    <&alloy::primitives::Uint<256, 4> as TryInto<u64>>::try_into(amount)
                    .map_err(|_| PyValueError::new_err("amount too big for u64"))
                })
                .collect::<Result<Vec<u64>, _>>()?,

                payment.price.erc721_addresses
                .iter()
                .map(|address| address.to_string())
                .collect::<Vec<String>>(),

                payment.price.erc721_ids
                    .iter()
                    .map(|amount| {
                        <&alloy::primitives::Uint<256, 4> as TryInto<u64>>::try_into(amount)
                        .map_err(|_| PyValueError::new_err("amount too big for u64"))
                })
                .collect::<Result<Vec<u64>, _>>()?,

                payment.arbiter.to_string(),
                payment.demand.result.to_string(),
            );
            Ok(result)
        },
    }
}

pub fn add_erc_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc_module = PyModule::new_bound(py, "erc")?;

    erc_module.add_function(wrap_pyfunction!(helloworld, &erc_module)?)?;

    erc_module.add_class::<BuyStatement>()?;
    erc_module.add_function(wrap_pyfunction!(get_buy_statement, &erc_module)?)?;

    parent_module.add_submodule(&erc_module)?;
    Ok(())
}
