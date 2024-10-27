use pyo3::prelude::*;

#[tokio::main]
#[pyfunction]
async fn helloworld() -> PyResult<String> {
    Ok("HelloWorld Bundle".into())
}

pub fn add_bundle_submodule(py: Python, parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    let bundle_module = PyModule::new_bound(py, "bundle")?;

    bundle_module.add_function(wrap_pyfunction!(helloworld, &bundle_module)?)?;

    parent_module.add_submodule(&bundle_module)?;
    Ok(())
}
