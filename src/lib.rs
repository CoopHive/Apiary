use pyo3::prelude::*;

pub mod contracts;
pub mod erc20_for_job;
pub mod erc721_for_job;
pub mod bundle_for_job;
pub mod erc_for_job;

pub mod provider;
pub mod apiary;
pub mod shared;

/// A Python module implemented in Rust.
#[pymodule]
fn apiars(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    erc_for_job::add_erc_submodule(py, m)?;
    erc20_for_job::add_erc20_submodule(py, m)?;
    erc721_for_job::add_erc721_submodule(py, m)?;
    bundle_for_job::add_bundle_submodule(py, m)?;
    
    Ok(())
}
