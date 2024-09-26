use alloy::{
    primitives::{b256, Address, Bytes, FixedBytes, U256},
    rpc::types::Filter,
    sol,
    sol_types::SolValue,
};
use alloy_provider::Provider;
use pyo3::{
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
};
use std::env;

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
    m.add_function(wrap_pyfunction!(helloworld, m)?)?;
    m.add_function(wrap_pyfunction!(make_buy_statement, m)?)?;
    m.add_function(wrap_pyfunction!(get_buy_statement, m)?)?;
    m.add_function(wrap_pyfunction!(submit_and_collect, m)?)?;
    m.add_function(wrap_pyfunction!(get_result_cid_from_sell_uid, m)?)?;
    Ok(())
}

fn py_val_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyValueError, _>(msg.into())
}

fn py_run_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyRuntimeError, _>(msg.into())
}

#[tokio::main]
#[pyfunction]
async fn make_buy_statement(
    token: String,
    amount: u64,
    query_cid: String,
    private_key: String,
) -> PyResult<String> {
    let provider = provider::get_provider(private_key)?;

    let token = Address::parse_checksummed(&token, None)
        .map_err(|_| py_val_err("couldn't parse token as an address"))?;
    let amount = U256::from(amount);
    let arbiter = env::var("DOCKER_RESULT_STATEMENT")
        .map_err(|_| py_val_err("DOCKER_RESULT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse DOCKER_RESULT_STATEMENT as an address"))?;
    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = DockerResultStatement::StatementData {
        resultCID: query_cid,
    }
    .abi_encode()
    .into();

    let payment_address = env::var("ERC20_PAYMENT_STATEMENT")
        .map_err(|_| py_val_err("ERC20_PAYMENT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse ERC20_PAYMENT_STATEMENT as an address"))?;
    // let eas_address = address!("4200000000000000000000000000000000000021");
    let eas_address = env::var("EAS_CONTRACT")
        .map_err(|_| py_val_err("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse EAS_CONTRACT as an address"))?;

    let token_contract = IERC20::new(token, &provider);
    let statement_contract = ERC20PaymentStatement::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, amount)
        .send()
        .await
        .map_err(|err| py_run_err(format!("error sending transaction; {:?}", err)))?
        .get_receipt()
        .await
        .map_err(|err| py_run_err(format!("error getting tx receipt; {:?}", err)))?;

    if !approval_receipt.status() {
        return Err(py_run_err("approval failed"));
    };

    let statement_hash = statement_contract
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
        .send()
        .await
        .map_err(|err| py_run_err(format!("{:?}", err)))?
        .watch()
        .await
        .map_err(|err| py_run_err(format!("{:?}", err)))?;

    let filter = Filter::new().address(eas_address).event_signature(b256!(
        "8bf46bf4cfd674fa735a3d63ec1c9ad4153f033c290341f3a588b75685141b35"
    ));

    let logs: Vec<_> = provider
        .get_logs(&filter)
        .await
        .map_err(|err| py_run_err(format!("error getting logs: {:?}", err)))?
        .into_iter()
        .filter(|log| log.transaction_hash == Some(statement_hash))
        .collect();

    let statement_uid = logs[0]
        .log_decode::<IEAS::Attested>()
        .map_err(|err| py_run_err(format!("couldn't decode attestation log; {:?}", err)))
        .map(|log| log.inner.uid)?;

    Ok(statement_uid.to_string())
}

#[tokio::main]
#[pyfunction]
async fn get_buy_statement(
    statement_uid: String,
    private_key: String,
) -> PyResult<(String, u64, String, String)> {
    let provider = provider::get_provider(private_key)?;

    let statement_uid: FixedBytes<32> = statement_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| py_val_err("couldn't parse statement_uid as bytes32"))?;

    let eas_address = env::var("EAS_CONTRACT")
        .map_err(|_| py_val_err("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse EAS_CONTRACT as an address"))?;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract
        .getAttestation(statement_uid)
        .call()
        .await
        .map_err(|err| py_run_err(format!("contract call to getAttestation failed; {:?}", err)))?
        ._0;

    let attestation_data =
        ERC20PaymentStatement::StatementData::abi_decode(attestation.data.as_ref(), true)
            .map_err(|_| py_run_err("attestation_data decoding failed"))?;

    let (token, amount, arbiter, demand) = (
        attestation_data.token,
        attestation_data.amount,
        attestation_data.arbiter,
        attestation_data.demand,
    );
    let amount: u64 = amount
        .try_into()
        .map_err(|_| py_run_err("amount too big for u64"))?;
    let demand = DockerResultStatement::StatementData::abi_decode(&demand, true)
        .map_err(|_| py_run_err("demand decoding failed"))?;

    Ok((
        token.to_string(),
        amount,
        arbiter.to_string(),
        demand.resultCID,
    ))
}

#[tokio::main]
#[pyfunction]
async fn get_result_cid_from_sell_uid(sell_uid: String, private_key: String) -> PyResult<String> {
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
        DockerResultStatement::StatementData::abi_decode(attestation.data.as_ref(), true)
            .map_err(|_| py_run_err("attestation_data decoding failed"))?;

    Ok(attestation_data.resultCID)
}

#[tokio::main]
#[pyfunction]
async fn submit_and_collect(
    buy_attestation_uid: String,
    result_cid: String,
    private_key: String,
) -> PyResult<String> {
    let provider = provider::get_provider(private_key)?;

    let buy_attestation_uid = buy_attestation_uid
        .parse::<FixedBytes<32>>()
        .map_err(|_| py_val_err("couldn't parse buy_attestation_uid as bytes32"))?;

    let result_address = env::var("DOCKER_RESULT_STATEMENT")
        .map_err(|_| py_val_err("DOCKER_RESULT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse DOCKER_RESULT_STATEMENT as an address"))?;
    let payment_address = env::var("ERC20_PAYMENT_STATEMENT")
        .map_err(|_| py_val_err("ERC20_PAYMENT_STATEMENT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse ERC20_PAYMENT_STATEMENT as an address"))?;
    let eas_address = env::var("EAS_CONTRACT")
        .map_err(|_| py_val_err("EAS_CONTRACT not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse EAS_CONTRACT as an address"))?;

    let result_contract = DockerResultStatement::new(result_address, &provider);
    let payment_contract = ERC20PaymentStatement::new(payment_address, &provider);

    let statement_hash = result_contract
        .makeStatement(
            DockerResultStatement::StatementData {
                resultCID: result_cid,
            },
            buy_attestation_uid,
        )
        .send()
        .await
        .map_err(|err| {
            py_run_err(format!(
                "contract call to result_contract make statement failed; {:?}",
                err
            ))
        })?
        .watch()
        .await
        .map_err(|err| py_run_err(format!("{:?}", err)))?;

    let filter = Filter::new().address(eas_address).event_signature(b256!(
        "8bf46bf4cfd674fa735a3d63ec1c9ad4153f033c290341f3a588b75685141b35"
    ));

    let logs: Vec<_> = provider
        .get_logs(&filter)
        .await
        .map_err(|err| py_run_err(format!("error getting logs: {:?}", err)))?
        .into_iter()
        .filter(|log| log.transaction_hash == Some(statement_hash))
        .collect();

    let sell_uid = logs[0]
        .log_decode::<IEAS::Attested>()
        .map_err(|err| py_run_err(format!("couldn't decode attestation log; {:?}", err)))
        .map(|log| log.inner.uid)?;

    let collect_receipt = payment_contract
        .collectPayment(buy_attestation_uid, sell_uid)
        .send()
        .await
        .map_err(|err| {
            py_run_err(format!(
                "contract call to collect payment failed; {:?}",
                err
            ))
        })?
        .get_receipt()
        .await
        .map_err(|err| py_run_err(format!("couldn't get receipt{:?}", err)))?;

    if collect_receipt.status() {
        Ok(sell_uid.to_string())
    } else {
        Err(py_run_err("contract call to collect payment failed"))
    }
}

#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld".into())
}
