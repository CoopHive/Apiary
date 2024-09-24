use alloy::{
    primitives::{b256, Address, Bytes, U256, FixedBytes},
    sol,
    sol_types::SolValue,
};
use pyo3::{
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
};
use std::env;

use eyre::eyre;

mod provider;

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC20PaymentStatement,
    "src/contracts/ERC20PaymentStatement.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    DockerResultStatement,
    "src/contracts/DockerResultStatement.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC20,
    "src/contracts/IERC20.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IEAS,
    "src/contracts/IEAS.json"
);

/// A Python module implemented in Rust.
#[pymodule]
fn apiars(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(make_buy_statement, m)?)?;
    m.add_function(wrap_pyfunction!(get_buy_statement, m)?)?;
    m.add_function(wrap_pyfunction!(submit_and_collect, m)?)?;
    m.add_function(wrap_pyfunction!(get_result_cid_from_sell_uid, m)?)?;
    m.add_function(wrap_pyfunction!(helloworld, m)?)?;
    Ok(())
}

#[macro_export]
macro_rules! py_val_err {
    ($msg:expr) => {
        Err(PyErr::new::<PyValueError, _>($msg))
    };
}

macro_rules! py_run_err {
    ($msg:expr) => {
        Err(PyErr::new::<PyRuntimeError, _>($msg))
    };
}

async fn approve_token(token: Address, amount: U256) -> eyre::Result<()> {
    let provider = provider::get_provider()?;

    let payment_address =
        env::var("ERC20_PAYMENT_STATEMENT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IERC20::new(token, provider);

    let receipt = contract.approve(payment_address, amount).call().await?._0;

    if receipt {Ok(())} else {Err(eyre!("TransactionFailed"))}
}

#[pyfunction]
async fn make_buy_statement(token: String, amount: u64, query_cid: String) -> PyResult<String> {
    let amount = U256::from(amount);

    let provider = provider::get_provider()?;
    let payment_address = env::var("ERC20_PAYMENT_STATEMENT")
        .or_else(|_| py_val_err!("ERC20_PAYMENT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse ERC20_PAYMENT_STATEMENT as an address"))?;
    
    approve_token(payment_address, amount).await
    .or_else(|_| py_run_err!("contract call to approve token failed"))?;

    let contract = ERC20PaymentStatement::new(payment_address, provider);

    let token = Address::parse_checksummed(token, None)
        .or_else(|_| py_val_err!("couldn't parse token as an address"))?;
    let arbiter = env::var("DOCKER_RESULT_STATEMENT")
        .or_else(|_| py_val_err!("DOCKER_RESULT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse DOCKER_RESULT_STATEMENT as an address"))?;
    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = DockerResultStatement::StatementData {
        resultCID: query_cid,
    }
    .abi_encode()
    .into();

    let statement_uid = contract
        .makeStatement(
            ERC20PaymentStatement::StatementData {
                token,
                amount,
                arbiter,
                demand,
            },
            0,
            b256!("0000000000000000000000000000000000000000000000000000000000000000"),
        )
        .call()
        .await
        .or_else(|_| py_run_err!("contract call to make payment statement failed"))?
        ._0;

    Ok(statement_uid.to_string())
}

#[pyfunction]
async fn get_buy_statement(statement_uid: String) -> PyResult<(String, u64, String, String)> {

    let statement_uid: FixedBytes<32> = statement_uid.parse::<FixedBytes<32>>().or_else(|_| py_val_err!("couldn't parse statement_uid as bytes32"))?;

    let provider = provider::get_provider()?;

    let eas_address =env::var("EAS_CONTRACT")
        .or_else(|_| py_val_err!("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse EAS_CONTRACT as an address"))?;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract.getAttestation(statement_uid).call()
    .await
    .or_else(|_| py_run_err!("contract call to getAttestation failed"))?
    ._0;

    let attestation_data = ERC20PaymentStatement::StatementData::abi_decode(attestation.data.as_ref(), true)
    .or_else(|_| py_run_err!("attestation_data decoding failed"))?;

    let (token, amount, arbiter, demand) = (attestation_data.token, attestation_data.amount, attestation_data.arbiter, attestation_data.demand);
    let amount: u64  = amount.try_into().or_else(|_| py_run_err!("amount too big for u64"))?;
    let demand = DockerResultStatement::StatementData::abi_decode(&demand, true)
    .or_else(|_| py_run_err!("demand decoding failed"))?;

    Ok((token.to_string(), amount, arbiter.to_string(), demand.resultCID))
}

#[pyfunction]
async fn get_result_cid_from_sell_uid(sell_uid: String) -> PyResult<String> {

    let sell_uid = sell_uid.parse::<FixedBytes<32>>().or_else(|_| py_val_err!("couldn't parse sell_uid as bytes32"))?;

    let provider = provider::get_provider()?;

    let eas_address =env::var("EAS_CONTRACT")
        .or_else(|_| py_val_err!("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse EAS_CONTRACT as an address"))?;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract.getAttestation(sell_uid).call()
    .await
    .or_else(|_| py_run_err!("contract call to getAttestation failed"))?
    ._0;

    let attestation_data = DockerResultStatement::StatementData::abi_decode(attestation.data.as_ref(), true)
    .or_else(|_| py_run_err!("attestation_data decoding failed"))?;

    Ok(attestation_data.resultCID)
}

#[pyfunction]
async fn submit_and_collect(buy_attestation_uid: String, result_cid: String) -> PyResult<String> {

    let buy_attestation_uid = buy_attestation_uid.parse::<FixedBytes<32>>().or_else(|_| py_val_err!("couldn't parse buy_attestation_uid as bytes32"))?;

    let provider = provider::get_provider()?;
    
    let result_address = env::var("DOCKER_RESULT_STATEMENT")
        .or_else(|_| py_val_err!("DOCKER_RESULT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse DOCKER_RESULT_STATEMENT as an address"))?;

    let payment_address = env::var("ERC20_PAYMENT_STATEMENT")
        .or_else(|_| py_val_err!("ERC20_PAYMENT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .or_else(|_| py_val_err!("couldn't parse ERC20_PAYMENT_STATEMENT as an address"))?;
    
    let result_contract = DockerResultStatement::new(result_address, provider.clone());
    let payment_contract = ERC20PaymentStatement::new(payment_address, provider);
    
    let sell_uid = result_contract.makeStatement(DockerResultStatement::StatementData{resultCID: result_cid}, buy_attestation_uid)
    .call()
    .await
    .or_else(|_| py_run_err!("contract call to result_contract make statement failed"))?
    ._0;

    let success = payment_contract.collectPayment(buy_attestation_uid, sell_uid)
    .call()
    .await.or_else(|_| py_run_err!("contract call to collect payment failed"))?._0;

    if success {Ok(sell_uid.to_string())} else {py_run_err!("contract call to collect payment failed")}
}

#[pyfunction]
async fn helloworld() -> PyResult<String>{
    Ok("HelloWorld".into())
}
