//! Thin PyO3 marshalling for the RF-04 scalar/fixed-grid/raw native slice.

use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyReadonlyArray1, PyReadonlyArray2, PyUntypedArrayMethods};
use pyo3::create_exception;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList};

use crate::kinetic::rf04_typeii::{
    parse_carrier, parse_quadrature_route, require_supported, scalar_raw_batch,
    scalar_raw_trajectory, ActionLedger, Rf04Error, ScalarBatch, ScalarDiagnostics,
    ScalarTrajectory, BATCH_ROUTE_ID, SCHEMA_ID, TRAJECTORY_ROUTE_ID,
};

create_exception!(bianchi_rustcore, RF04InputError, PyValueError);
create_exception!(bianchi_rustcore, RF04CapabilityError, PyValueError);
create_exception!(bianchi_rustcore, RF04PhysicalDomainError, PyValueError);
create_exception!(bianchi_rustcore, RF04CertificateError, PyRuntimeError);
create_exception!(bianchi_rustcore, RF04MemberError, PyRuntimeError);

const EXECUTION_IDENTITY: &str = r#"{"authority_ids":{"background":"SCI-AUTH-04-BACKGROUND-V1","collision":"SCI-AUTH-04-COLLISION-V1","kato":"SCI-AUTH-04-KATO-V1","projector":"SCI-AUTH-04-PROJECTOR-V1","thermodynamics":"SCI-AUTH-04-THERMODYNAMICS-V1"},"carrier_capabilities":["scalar_intensity_v1"],"certificate_scope":"PROJECTED_RESIDUAL_ONLY_NOT_GLOBAL_FORWARD_ERROR","diagnostic_semantics":{"equilibrium_null_residual":"ALIAS_OF_RIGHT_KERNEL_RESIDUAL_NOT_INDEPENDENT_EVIDENCE","left_invariant_drift":"FULL_STEP_MIDPOINT_LEFT_COVECTOR_DRIFT_INCLUDES_TRANSPORT","positivity_margin":"MINIMUM_SCALAR_INTENSITY_PER_ACCEPTED_HISTORY_ROW","projected_residual_estimate":"MAX_ACCEPTED_PROJECTED_RESIDUAL_TARGET_RATIO_NOT_FORWARD_ERROR","projector_idempotence_residual":"MAX_ABS_P_SQUARED_MINUS_P","right_kernel_residual":"NORM_INF_C_RAW_R_OVER_NORM_INF_R"},"execution_profile_id":"rf04-scalar-fixed-node-raw-slice/v1","execution_profile_sha256":"56ef82909ed00e3bfe40080e03d11a264b895f7da28dc5d24d51c5ae2c7f7de3","identity_schema":"bass-rf04-typeii-execution-identity/v1","native_payload_identity":"bass-rf04-scalar-raw-native-v1","physical_guard_fingerprint":"6bf35989f4c3e9eb2dc453b1db4a6898f1a06191d05f88acdd4f782439ae4483","public_route_schema_sha256":"be2c73e07e5a8179c10ec4aab058915b79b1d7ab87fc624d65e5e0d34d94d097","quadrature_capabilities":["fixed_grid_raw_v1"],"route_capability_fingerprint":"dfd0556a86c1f3f98ff6f25960436a18335c92f9b32e9bcbd9d41c03253e8282","sci_auth_head":"1298c2ef8cc8eaca8edcd99332653c8a1cbc1c86","sci_auth_manifest_sha256":"9c646d7fa43463484e832349f0a4ae9c3728dc1d68a2370504facdc41aad9b9f","sci_auth_tree":"37edaaea720a3197881b94bc39413787db091432","source_owner_blob_sha1":"e1b2016d1a3694d6552eef78450853df32f22163","supported_combinations":[["scalar_intensity_v1","fixed_grid_raw_v1"]]}"#;

pub(crate) fn map_rf04_error(error: Rf04Error) -> PyErr {
    let message = error.to_string();
    match error {
        Rf04Error::Input { .. } => RF04InputError::new_err(message),
        Rf04Error::Capability { .. } => RF04CapabilityError::new_err(message),
        Rf04Error::PhysicalDomain { .. } => RF04PhysicalDomainError::new_err(message),
        Rf04Error::Certificate { .. } => RF04CertificateError::new_err(message),
        Rf04Error::Member { .. } => RF04MemberError::new_err(message),
    }
}

fn vector_from_python(value: &Bound<'_, PyAny>, name: &str) -> PyResult<Vec<f64>> {
    let array = value.extract::<PyReadonlyArray1<'_, f64>>().map_err(|_| {
        RF04InputError::new_err(format!("{name} must be a contiguous float64 vector"))
    })?;
    array
        .as_slice()
        .map(|values| values.to_vec())
        .map_err(|_| RF04InputError::new_err(format!("{name} must be C-contiguous")))
}

fn matrix_from_python(value: &Bound<'_, PyAny>, name: &str) -> PyResult<Vec<Vec<f64>>> {
    let array = value.extract::<PyReadonlyArray2<'_, f64>>().map_err(|_| {
        RF04InputError::new_err(format!("{name} must be a contiguous float64 matrix"))
    })?;
    let shape = array.shape();
    let rows = shape[0];
    let columns = shape[1];
    let values = array
        .as_slice()
        .map_err(|_| RF04InputError::new_err(format!("{name} must be C-contiguous")))?;
    Ok((0..rows)
        .map(|row| values[row * columns..(row + 1) * columns].to_vec())
        .collect())
}

fn fixed_rows_from_python<const N: usize>(
    value: &Bound<'_, PyAny>,
    name: &str,
) -> PyResult<Vec<[f64; N]>> {
    let rows = matrix_from_python(value, name)?;
    rows.into_iter()
        .map(|row| {
            row.try_into().map_err(|row: Vec<f64>| {
                RF04InputError::new_err(format!(
                    "{name} must have exactly {N} columns; observed {}",
                    row.len()
                ))
            })
        })
        .collect()
}

fn ledger_to_python<'py>(py: Python<'py>, ledger: &[ActionLedger]) -> PyResult<Bound<'py, PyList>> {
    let output = PyList::empty(py);
    for entry in ledger {
        let item = PyDict::new(py);
        item.set_item("accepted_steps", entry.accepted_steps)?;
        item.set_item("rejected_steps", entry.rejected_steps)?;
        item.set_item("nonfinite_rejections", entry.nonfinite_rejections)?;
        item.set_item("matvecs", entry.matvecs)?;
        item.set_item("projected_exponentials", entry.projected_exponentials)?;
        item.set_item("max_basis", entry.max_basis)?;
        item.set_item("final_basis", entry.final_basis)?;
        item.set_item("max_attempt_error_ratio", entry.max_attempt_error_ratio)?;
        item.set_item("max_accepted_error_ratio", entry.max_accepted_error_ratio)?;
        item.set_item("last_accepted_error_ratio", entry.last_accepted_error_ratio)?;
        item.set_item("target_semantics", entry.target_semantics)?;
        output.append(item)?;
    }
    Ok(output)
}

fn diagnostics_to_python<'py>(
    py: Python<'py>,
    diagnostics: ScalarDiagnostics,
) -> PyResult<Bound<'py, PyDict>> {
    let output = PyDict::new(py);
    output.set_item(
        "equilibrium_null_residual",
        Array1::from_vec(diagnostics.equilibrium_null_residual).into_pyarray(py),
    )?;
    output.set_item(
        "right_kernel_residual",
        Array1::from_vec(diagnostics.right_kernel_residual).into_pyarray(py),
    )?;
    output.set_item(
        "left_invariant_drift",
        Array1::from_vec(diagnostics.left_invariant_drift).into_pyarray(py),
    )?;
    output.set_item(
        "projected_residual_estimate",
        Array1::from_vec(diagnostics.projected_residual_estimate).into_pyarray(py),
    )?;
    output.set_item(
        "projector_idempotence_residual",
        Array1::from_vec(diagnostics.projector_idempotence_residual).into_pyarray(py),
    )?;
    output.set_item(
        "positivity_margin",
        Array1::from_vec(diagnostics.positivity_margin).into_pyarray(py),
    )?;
    output.set_item(
        "action_ledger",
        ledger_to_python(py, &diagnostics.action_ledger)?,
    )?;
    Ok(output)
}

fn trajectory_to_python<'py>(
    py: Python<'py>,
    result: ScalarTrajectory,
) -> PyResult<Bound<'py, PyDict>> {
    let rows = result.radiation_history.len();
    let columns = result.radiation_history[0].len();
    let flat = result.radiation_history.into_iter().flatten().collect();
    let history = Array2::from_shape_vec((rows, columns), flat)
        .expect("validated RF-04 trajectory history shape");
    let output = PyDict::new(py);
    output.set_item("schema_id", SCHEMA_ID)?;
    output.set_item("route_id", TRAJECTORY_ROUTE_ID)?;
    output.set_item("execution_identity", EXECUTION_IDENTITY)?;
    output.set_item("radiation_history", history.into_pyarray(py))?;
    output.set_item(
        "diagnostics",
        diagnostics_to_python(py, result.diagnostics)?,
    )?;
    Ok(output)
}

fn batch_to_python<'py>(py: Python<'py>, result: ScalarBatch) -> PyResult<Bound<'py, PyDict>> {
    let rows = result.final_radiation.len();
    let columns = result.final_radiation[0].len();
    let flat = result.final_radiation.into_iter().flatten().collect();
    let final_radiation =
        Array2::from_shape_vec((rows, columns), flat).expect("validated RF-04 batch output shape");
    let error_codes = PyList::empty(py);
    for code in result.member_error_code {
        match code {
            Some(code) => error_codes.append(code)?,
            None => error_codes.append(py.None())?,
        }
    }
    let output = PyDict::new(py);
    output.set_item("schema_id", SCHEMA_ID)?;
    output.set_item("route_id", BATCH_ROUTE_ID)?;
    output.set_item("execution_identity", EXECUTION_IDENTITY)?;
    output.set_item("final_radiation", final_radiation.into_pyarray(py))?;
    output.set_item(
        "member_status",
        Array1::from_vec(result.member_status).into_pyarray(py),
    )?;
    output.set_item(
        "member_completed_steps",
        Array1::from_vec(result.member_completed_steps).into_pyarray(py),
    )?;
    output.set_item("member_error_code", error_codes)?;
    Ok(output)
}

#[pyfunction]
pub(crate) fn rf04_typeii_execution_identity_v1() -> &'static str {
    EXECUTION_IDENTITY
}

#[pyfunction]
#[pyo3(signature = (initial_radiation, directions, weights, background_q1, background_mid, background_q3, opacity_mid, step_size, gamma, opacity_scale, tilt_axis, carrier, quadrature_route))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn rf04_typeii_trajectory_v1<'py>(
    py: Python<'py>,
    initial_radiation: &Bound<'_, PyAny>,
    directions: &Bound<'_, PyAny>,
    weights: &Bound<'_, PyAny>,
    background_q1: &Bound<'_, PyAny>,
    background_mid: &Bound<'_, PyAny>,
    background_q3: &Bound<'_, PyAny>,
    opacity_mid: &Bound<'_, PyAny>,
    step_size: &Bound<'_, PyAny>,
    gamma: f64,
    opacity_scale: f64,
    tilt_axis: usize,
    carrier: &str,
    quadrature_route: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let carrier = parse_carrier(carrier).map_err(map_rf04_error)?;
    let route = parse_quadrature_route(quadrature_route).map_err(map_rf04_error)?;
    require_supported(carrier, route).map_err(map_rf04_error)?;
    let initial = vector_from_python(initial_radiation, "initial_radiation")?;
    let directions = fixed_rows_from_python::<3>(directions, "directions")?;
    let weights = vector_from_python(weights, "weights")?;
    let q1 = fixed_rows_from_python::<5>(background_q1, "background_q1")?;
    let mid = fixed_rows_from_python::<5>(background_mid, "background_mid")?;
    let q3 = fixed_rows_from_python::<5>(background_q3, "background_q3")?;
    let opacity = vector_from_python(opacity_mid, "opacity_mid")?;
    let step = vector_from_python(step_size, "step_size")?;
    let result = py
        .detach(move || {
            scalar_raw_trajectory(
                &initial,
                &directions,
                &weights,
                &q1,
                &mid,
                &q3,
                &opacity,
                &step,
                gamma,
                opacity_scale,
                tilt_axis,
            )
        })
        .map_err(map_rf04_error)?;
    trajectory_to_python(py, result)
}

#[pyfunction]
#[pyo3(signature = (initial_radiation_batch, directions, weights, background_q1, background_mid, background_q3, opacity_mid, step_size, gamma, opacity_scale, tilt_axis, carrier, quadrature_route))]
#[allow(clippy::too_many_arguments)]
pub(crate) fn rf04_typeii_batch_v1<'py>(
    py: Python<'py>,
    initial_radiation_batch: &Bound<'_, PyAny>,
    directions: &Bound<'_, PyAny>,
    weights: &Bound<'_, PyAny>,
    background_q1: &Bound<'_, PyAny>,
    background_mid: &Bound<'_, PyAny>,
    background_q3: &Bound<'_, PyAny>,
    opacity_mid: &Bound<'_, PyAny>,
    step_size: &Bound<'_, PyAny>,
    gamma: f64,
    opacity_scale: f64,
    tilt_axis: usize,
    carrier: &str,
    quadrature_route: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let carrier = parse_carrier(carrier).map_err(map_rf04_error)?;
    let route = parse_quadrature_route(quadrature_route).map_err(map_rf04_error)?;
    require_supported(carrier, route).map_err(map_rf04_error)?;
    let initial = matrix_from_python(initial_radiation_batch, "initial_radiation_batch")?;
    let directions = fixed_rows_from_python::<3>(directions, "directions")?;
    let weights = vector_from_python(weights, "weights")?;
    let q1 = fixed_rows_from_python::<5>(background_q1, "background_q1")?;
    let mid = fixed_rows_from_python::<5>(background_mid, "background_mid")?;
    let q3 = fixed_rows_from_python::<5>(background_q3, "background_q3")?;
    let opacity = vector_from_python(opacity_mid, "opacity_mid")?;
    let step = vector_from_python(step_size, "step_size")?;
    let result = py
        .detach(move || {
            scalar_raw_batch(
                &initial,
                &directions,
                &weights,
                &q1,
                &mid,
                &q3,
                &opacity,
                &step,
                gamma,
                opacity_scale,
                tilt_axis,
            )
        })
        .map_err(map_rf04_error)?;
    batch_to_python(py, result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rf04_scalar_raw_identity_is_canonical_and_partial() {
        assert!(EXECUTION_IDENTITY.contains("\"carrier_capabilities\":[\"scalar_intensity_v1\"]"));
        assert!(EXECUTION_IDENTITY.contains("\"quadrature_capabilities\":[\"fixed_grid_raw_v1\"]"));
        assert!(!EXECUTION_IDENTITY.contains("polarized_rank9_v1"));
        assert!(!EXECUTION_IDENTITY.contains("fixed_grid_ap_corrected_v1"));
    }
}
