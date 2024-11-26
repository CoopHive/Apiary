use alloy::{primitives::{Address, U256}, sol};
use pyo3::{
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
};
pub struct ERC20Price {
    pub token: Address,
    pub amount: U256,
}

pub struct ERC721Price {
    pub token: Address,
    pub id: U256,
}

pub struct BundlePrice {
    pub erc20_addresses: Vec<Address>,
    pub erc20_amounts: Vec<U256>,
    pub erc721_addresses: Vec<Address>,
    pub erc721_ids: Vec<U256>,
}

sol!{
    struct DemandData {
        string job_cid;
        string job_input_cid;
    }
 }

pub fn py_val_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyValueError, _>(msg.into())
}

pub fn py_run_err(msg: impl Into<String>) -> PyErr {
    PyErr::new::<PyRuntimeError, _>(msg.into())
}
