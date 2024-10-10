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
#[pyo3(name = "helloworld")]
async fn erc721_helloworld() -> PyResult<String> {
    Ok("HelloWorld ERC721".into())
}

#[tokio::main]
#[pyfunction]
#[pyo3(name = "make_buy_statement")]
async fn erc_721_make_buy_statement(
    token: String,
    token_id: u64,
    query: String,
    private_key: String,
) -> PyResult<String>{

    let provider = provider::get_provider(private_key)?;

    let token_address = Address::parse_checksummed(&token, None)
        .map_err(|_| py_val_err("couldn't parse token as an address"))?;

    let token_id = U256::from(token_id);
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

    let payment_address = env::var("ERC721_PAYMENT_OBLIGATION")
        .map_err(|_| py_val_err("ERC721_PAYMENT_OBLIGATION not set"))
        .map(|a| Address::parse_checksummed(a, None))?
        .map_err(|_| py_val_err("couldn't parse ERC721_PAYMENT_OBLIGATION as an address"))?;

    let token_contract = IERC721::new(token_address, &provider);
    let statement_contract = ERC721PaymentObligation::new(payment_address, &provider);

    let approval_receipt = token_contract
        .approve(payment_address, token_id)
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
            ERC721PaymentObligation::StatementData {
                token: token_address,
                tokenId: token_id,
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

pub fn add_erc721_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let erc721_module = PyModule::new_bound(py, "erc721")?;
    
    erc721_module.add_function(wrap_pyfunction!(erc721_helloworld, erc721_module.clone())?)?;
    erc721_module.add_function(wrap_pyfunction!(erc_721_make_buy_statement, erc721_module.clone())?)?;

    parent_module.add_submodule(&erc721_module)?;
    Ok(())
}
