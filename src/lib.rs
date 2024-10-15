use pyo3::prelude::*;

pub mod erc20_for_job;
pub mod erc721_for_job;
pub mod provider;
pub mod shared;
pub mod standalone;

/// A Python module implemented in Rust.
#[pymodule]
fn apiars(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    erc20_for_job::add_erc20_submodule(py, m)?;
    erc721_for_job::add_erc721_submodule(py, m)?;

    m.add_function(wrap_pyfunction!(shared::get_result_cid_from_sell_uid, m)?)?;
    Ok(())
}
