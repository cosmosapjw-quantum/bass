//! Thin PyO3 adapter for RF-03 finite-boost invariants.

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

use crate::matter::MatterState;
use crate::tilt::tilt_invariants;

use super::rf03_matter::{map_matter_error, scalar_from_python, vector_from_python};

#[pyfunction]
pub(crate) fn rf03_tilt_invariants<'py>(
    py: Python<'py>,
    omega: &Bound<'_, PyAny>,
    v: &Bound<'_, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let omega = scalar_from_python(omega, "Omega")?;
    let v = vector_from_python::<3>(v, "v")?;
    let state = MatterState::new(omega, v).map_err(map_matter_error)?;
    let observed = tilt_invariants(state).map_err(map_matter_error)?;
    let output = PyDict::new(py);
    output.set_item("lorentz_gamma", observed.lorentz_gamma)?;
    output.set_item("u_norm_residual", observed.u_norm_residual)?;
    output.set_item("density_margin", observed.density_margin)?;
    output.set_item("tilt_margin", observed.tilt_margin)?;
    Ok(output)
}
