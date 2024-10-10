use alloy::{
    primitives::{b256, Address, Bytes, FixedBytes, U256},
    sol,
    sol_types::{SolEvent, SolValue},
};
use pyo3::prelude::*;
use std::env;

use crate::provider;
use crate::shared::{JobResultObligation, IEAS, py_val_err, py_run_err};

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC20PaymentObligation,
    "src/contracts/ERC20PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC20,
    "src/contracts/IERC20.json"
);

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
    let provider = provider::get_provider(private_key)?;

    let token_address = Address::parse_checksummed(&token, None)
        .map_err(|_| py_val_err("couldn't parse token as an address"))?;
    let amount = U256::from(amount);
    let arbiter = env::var("TRIVIAL_ARBITER")
        .map_err(|_| py_val_err("TRIVIAL_ARBITER not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse TRIVIAL_ARBITER as an address"))?;
    // ResultData and StatementData became the same abi type after solc compilation
    // since they have the same structure: (string)
    let demand: Bytes = JobResultObligation::StatementData {
        result: query,
    }
    .abi_encode()
    .into();

    let payment_address = env::var("ERC20_PAYMENT_OBLIGATION")
        .map_err(|_| py_val_err("ERC20_PAYMENT_OBLIGATION not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse ERC20_PAYMENT_OBLIGATION as an address"))?;

    let token_contract = IERC20::new(token_address, &provider);
    let statement_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, amount)
        .send()
        .await
        .map_err(|err| py_run_err(format!("error calling approve; {:?}", err)))?
        .get_receipt()
        .await
        .map_err(|err| py_run_err(format!("error getting approval receipt; {:?}", err)))?;

    if !approval_receipt.status() {
        return Err(py_run_err("approval failed"));
    };

    let log = statement_contract
        .makeStatement(
            ERC20PaymentObligation::StatementData {
                token: token_address,
                amount,
                arbiter,
                demand,
            },
            0,
            b256!("0000000000000000000000000000000000000000000000000000000000000000"),
        )
        .send()
        .await
        .map_err(|err| py_run_err(format!("error calling makeStatement (buy); {:?}", err)))?
        .get_receipt()
        .await
        .map_err(|err| py_run_err(format!("error getting buy statement receipt; {:?}", err)))?
        .inner
        .logs()
        .into_iter()
        .filter(|log| log.topic0() == Some(&IEAS::Attested::SIGNATURE_HASH))
        .collect::<Vec<_>>()
        .get(0)
        .map_or(
            Err(py_run_err("makeStatement logs didn't contain Attest")),
            |log| {
                log.log_decode::<IEAS::Attested>().map_err(|err| {
                    py_run_err(format!("couldn't decode attestation log; {:?}", err))
                })
            },
        )?;

    Ok(log.inner.uid.to_string())
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
        ERC20PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)
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
    let demand = JobResultObligation::StatementData::abi_decode(&demand, true)
        .map_err(|_| py_run_err("demand decoding failed"))?;

    Ok((
        token.to_string(),
        amount,
        arbiter.to_string(),
        demand.result,
    ))
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

    let result_address = env::var("JOB_RESULT_OBLIGATION")
        .map_err(|_| py_val_err("JOB_RESULT_OBLIGATION not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse JOB_RESULT_OBLIGATION as an address"))?;
    let payment_address = env::var("ERC20_PAYMENT_OBLIGATION")
        .map_err(|_| py_val_err("ERC20_PAYMENT_OBLIGATION not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse ERC20_PAYMENT_OBLIGATION as an address"))?;

    let result_contract = JobResultObligation::new(result_address, &provider);
    let payment_contract = ERC20PaymentObligation::new(payment_address, &provider);

    let sell_uid = result_contract
        .makeStatement(
            JobResultObligation::StatementData {
                result: result_cid,
            },
            buy_attestation_uid,
        )
        .send()
        .await
        .map_err(|err| py_run_err(format!("error calling makeStatement (sell); {:?}", err)))?
        .get_receipt()
        .await
        .map_err(|err| py_run_err(format!("error getting sell statement receipt; {:?}", err)))?
        .inner
        .logs()
        .into_iter()
        .filter(|log| log.topic0() == Some(&IEAS::Attested::SIGNATURE_HASH))
        .collect::<Vec<_>>()
        .get(0)
        .map_or(
            Err(py_run_err("makeStatement logs didn't contain Attest")),
            |log| {
                log.log_decode::<IEAS::Attested>()
                    .map_err(|err| {
                        py_run_err(format!("couldn't decode attestation log; {:?}", err))
                    })
                    .map(|a| a.inner.uid)
            },
        )?;

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
        .map_err(|err| py_run_err(format!("couldn't get collection receipt; {:?}", err)))?;

    if collect_receipt.status() {
        Ok(sell_uid.to_string())
    } else {
        Err(py_run_err("contract call to collect payment failed"))
    }
}

pub fn add_erc20_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc20_module = PyModule::new_bound(py, "erc20")?;
    
    erc20_module.add_function(wrap_pyfunction!(helloworld, erc20_module.clone())?)?;
    erc20_module.add_function(wrap_pyfunction!(make_buy_statement, erc20_module.clone())?)?;
    erc20_module.add_function(wrap_pyfunction!(get_buy_statement, erc20_module.clone())?)?;
    erc20_module.add_function(wrap_pyfunction!(submit_and_collect, erc20_module.clone())?)?;

    parent_module.add_submodule(&erc20_module)?;
    Ok(())
}
