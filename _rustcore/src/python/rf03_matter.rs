//! Thin PyO3 adapter for the RF-03 explicit gamma-law matter core.

use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1, PyReadonlyArray2, PyReadonlyArray3};
use pyo3::create_exception;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

use crate::matter::{
    force, force_jvp, integrate_context_history, integrate_fixed_context, GammaLawModel,
    MatterContext, MatterDirection, MatterError, MatterState,
};

create_exception!(bianchi_rustcore, RF03ModelError, PyValueError);
create_exception!(bianchi_rustcore, RF03DomainError, PyValueError);
create_exception!(bianchi_rustcore, RF03InputError, PyValueError);

pub(crate) fn map_matter_error(error: MatterError) -> PyErr {
    match error {
        MatterError::Model(detail) => RF03ModelError::new_err(detail),
        MatterError::Domain(detail) => RF03DomainError::new_err(detail),
        MatterError::Input(detail) => RF03InputError::new_err(detail),
    }
}

fn model_from_python(
    model_id: &Bound<'_, PyAny>,
    gamma: &Bound<'_, PyAny>,
) -> PyResult<GammaLawModel> {
    if model_id.is_none() {
        return Err(RF03ModelError::new_err(
            "model_id is required and cannot be None",
        ));
    }
    let model_id = model_id.extract::<String>().map_err(|_| {
        RF03ModelError::new_err("model_id must be the exact RF-03 production model string")
    })?;
    if model_id != crate::matter::EXPLICIT_GAMMA_LAW_MODEL_ID {
        return Err(map_matter_error(MatterError::Model(format!(
            "unsupported RF-03 model_id {model_id:?}"
        ))));
    }
    let gamma = gamma
        .extract::<f64>()
        .map_err(|_| RF03InputError::new_err("gamma must be a scalar float"))?;
    GammaLawModel::select(&model_id, gamma).map_err(map_matter_error)
}

pub(super) fn scalar_from_python(value: &Bound<'_, PyAny>, name: &str) -> PyResult<f64> {
    value
        .extract::<f64>()
        .map_err(|_| RF03InputError::new_err(format!("{name} must be a scalar float")))
}

pub(super) fn vector_from_python<const N: usize>(
    value: &Bound<'_, PyAny>,
    name: &str,
) -> PyResult<[f64; N]> {
    let array = value.extract::<PyReadonlyArray1<'_, f64>>().map_err(|_| {
        RF03InputError::new_err(format!("{name} must be a contiguous float64 vector"))
    })?;
    let values = array.as_slice().map_err(|_| {
        RF03InputError::new_err(format!("{name} must be a contiguous float64 vector"))
    })?;
    values
        .try_into()
        .map_err(|_| RF03InputError::new_err(format!("{name} must have exactly {N} components")))
}

fn matrix_from_python(value: &Bound<'_, PyAny>, name: &str) -> PyResult<[[f64; 3]; 3]> {
    let array = value
        .extract::<PyReadonlyArray2<'_, f64>>()
        .map_err(|_| RF03InputError::new_err(format!("{name} must be a float64 matrix")))?;
    let view = array.as_array();
    if view.shape() != [3, 3] {
        return Err(RF03InputError::new_err(format!(
            "{name} must have shape (3, 3)"
        )));
    }
    Ok(std::array::from_fn(|row| {
        std::array::from_fn(|column| view[[row, column]])
    }))
}

fn context_from_python(
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
) -> PyResult<MatterContext> {
    MatterContext::new(
        matrix_from_python(sigma, "Sigma")?,
        matrix_from_python(n, "N")?,
        vector_from_python(a, "A")?,
        vector_from_python(r, "R")?,
        scalar_from_python(q, "q")?,
    )
    .map_err(map_matter_error)
}

fn state_from_python(state: &Bound<'_, PyAny>) -> PyResult<MatterState> {
    let state = vector_from_python::<4>(state, "state")?;
    MatterState::new(state[0], [state[1], state[2], state[3]]).map_err(map_matter_error)
}

fn direction_from_python(direction: &Bound<'_, PyAny>) -> PyResult<MatterDirection> {
    let direction = vector_from_python::<4>(direction, "direction")?;
    MatterDirection::new(direction[0], [direction[1], direction[2], direction[3]])
        .map_err(map_matter_error)
}

fn validate_read_only_temperature(value: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
    if let Some(value) = value {
        if value.is_none() {
            return Ok(());
        }
        let temperature = scalar_from_python(value, "T_gamma")?;
        if !temperature.is_finite() {
            return Err(RF03InputError::new_err(
                "T_gamma must be finite when supplied",
            ));
        }
    }
    Ok(())
}

fn context_history_from_python(
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
) -> PyResult<Vec<MatterContext>> {
    let sigma = sigma.extract::<PyReadonlyArray3<'_, f64>>().map_err(|_| {
        RF03InputError::new_err("Sigma history must be a float64 array with shape (M,3,3)")
    })?;
    let n = n.extract::<PyReadonlyArray3<'_, f64>>().map_err(|_| {
        RF03InputError::new_err("N history must be a float64 array with shape (M,3,3)")
    })?;
    let a = a.extract::<PyReadonlyArray2<'_, f64>>().map_err(|_| {
        RF03InputError::new_err("A history must be a float64 array with shape (M,3)")
    })?;
    let r = r.extract::<PyReadonlyArray2<'_, f64>>().map_err(|_| {
        RF03InputError::new_err("R history must be a float64 array with shape (M,3)")
    })?;
    let q = q
        .extract::<PyReadonlyArray1<'_, f64>>()
        .map_err(|_| RF03InputError::new_err("q history must be a contiguous float64 vector"))?;
    let sigma_view = sigma.as_array();
    let n_view = n.as_array();
    let a_view = a.as_array();
    let r_view = r.as_array();
    let q_values = q
        .as_slice()
        .map_err(|_| RF03InputError::new_err("q history must be contiguous"))?;
    let count = q_values.len();
    if sigma_view.shape() != [count, 3, 3]
        || n_view.shape() != [count, 3, 3]
        || a_view.shape() != [count, 3]
        || r_view.shape() != [count, 3]
    {
        return Err(RF03InputError::new_err(
            "Sigma,N,A,R,q histories must share M and have shapes (M,3,3),(M,3,3),(M,3),(M,3),(M,)",
        ));
    }
    (0..count)
        .map(|sample| {
            MatterContext::new(
                std::array::from_fn(|row| {
                    std::array::from_fn(|column| sigma_view[[sample, row, column]])
                }),
                std::array::from_fn(|row| {
                    std::array::from_fn(|column| n_view[[sample, row, column]])
                }),
                std::array::from_fn(|index| a_view[[sample, index]]),
                std::array::from_fn(|index| r_view[[sample, index]]),
                q_values[sample],
            )
            .map_err(map_matter_error)
        })
        .collect()
}

fn validate_temperature_history(value: Option<&Bound<'_, PyAny>>, expected: usize) -> PyResult<()> {
    let Some(value) = value else {
        return Ok(());
    };
    if value.is_none() {
        return Ok(());
    }
    let history = value.extract::<PyReadonlyArray1<'_, f64>>().map_err(|_| {
        RF03InputError::new_err("T_gamma history must be a contiguous float64 vector")
    })?;
    let values = history
        .as_slice()
        .map_err(|_| RF03InputError::new_err("T_gamma history must be contiguous"))?;
    if values.len() != expected || values.iter().any(|entry| !entry.is_finite()) {
        return Err(RF03InputError::new_err(
            "T_gamma history must contain M finite samples",
        ));
    }
    Ok(())
}

fn integration_result_to_python<'py>(
    py: Python<'py>,
    result: crate::matter::IntegrationResult,
) -> PyResult<Bound<'py, PyDict>> {
    let flat_states: Vec<f64> = result.states.iter().flatten().copied().collect();
    let states = Array2::from_shape_vec((result.states.len(), 4), flat_states)
        .expect("RF-03 state history shape");
    let output = PyDict::new(py);
    output.set_item("times", Array1::from_vec(result.times).into_pyarray(py))?;
    output.set_item("states", states.into_pyarray(py))?;
    output.set_item("status", result.terminal.code())?;
    output.set_item(
        "terminal_index",
        result.terminal.terminal_index(result.states.len() - 1),
    )?;
    output.set_item("terminal_detail", result.terminal.detail())?;
    output.set_item("model_id", crate::matter::EXPLICIT_GAMMA_LAW_MODEL_ID)?;
    output.set_item("state_order", ("Omega", "v1", "v2", "v3"))?;
    Ok(output)
}

#[pyfunction]
#[pyo3(signature = (model_id, gamma, state, sigma, n, a, r, q, t_gamma=None))]
pub(crate) fn rf03_matter_force<'py>(
    py: Python<'py>,
    model_id: &Bound<'_, PyAny>,
    gamma: &Bound<'_, PyAny>,
    state: &Bound<'_, PyAny>,
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
    t_gamma: Option<&Bound<'_, PyAny>>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let model = model_from_python(model_id, gamma)?;
    let state = state_from_python(state)?;
    let context = context_from_python(sigma, n, a, r, q)?;
    validate_read_only_temperature(t_gamma)?;
    let observed = force(model, state, context).map_err(map_matter_error)?;
    Ok(Array1::from_vec(observed.as_array().to_vec()).into_pyarray(py))
}

#[pyfunction]
#[pyo3(signature = (model_id, gamma, state, direction, sigma, n, a, r, q, t_gamma=None))]
pub(crate) fn rf03_matter_force_jvp<'py>(
    py: Python<'py>,
    model_id: &Bound<'_, PyAny>,
    gamma: &Bound<'_, PyAny>,
    state: &Bound<'_, PyAny>,
    direction: &Bound<'_, PyAny>,
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
    t_gamma: Option<&Bound<'_, PyAny>>,
) -> PyResult<(Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>)> {
    let model = model_from_python(model_id, gamma)?;
    let state = state_from_python(state)?;
    let direction = direction_from_python(direction)?;
    let context = context_from_python(sigma, n, a, r, q)?;
    validate_read_only_temperature(t_gamma)?;
    let (primal, tangent) =
        force_jvp(model, state, direction, context).map_err(map_matter_error)?;
    Ok((
        Array1::from_vec(primal.as_array().to_vec()).into_pyarray(py),
        Array1::from_vec(tangent.as_array().to_vec()).into_pyarray(py),
    ))
}

#[pyfunction]
#[pyo3(signature = (model_id, gamma, state, sigma, n, a, r, q, t_end, nsteps, t_gamma=None))]
pub(crate) fn rf03_matter_integrate<'py>(
    py: Python<'py>,
    model_id: &Bound<'_, PyAny>,
    gamma: &Bound<'_, PyAny>,
    state: &Bound<'_, PyAny>,
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
    t_end: &Bound<'_, PyAny>,
    nsteps: &Bound<'_, PyAny>,
    t_gamma: Option<&Bound<'_, PyAny>>,
) -> PyResult<Bound<'py, PyDict>> {
    let model = model_from_python(model_id, gamma)?;
    let state = state_from_python(state)?;
    let context = context_from_python(sigma, n, a, r, q)?;
    let t_end = scalar_from_python(t_end, "t_end")?;
    let nsteps = nsteps
        .extract::<usize>()
        .map_err(|_| RF03InputError::new_err("nsteps must be a positive integer"))?;
    validate_read_only_temperature(t_gamma)?;
    let result =
        integrate_fixed_context(model, state, context, t_end, nsteps).map_err(map_matter_error)?;
    integration_result_to_python(py, result)
}

#[pyfunction]
#[pyo3(signature = (model_id, gamma, state, times, sigma, n, a, r, q, t_gamma=None))]
pub(crate) fn rf03_matter_integrate_history<'py>(
    py: Python<'py>,
    model_id: &Bound<'_, PyAny>,
    gamma: &Bound<'_, PyAny>,
    state: &Bound<'_, PyAny>,
    times: &Bound<'_, PyAny>,
    sigma: &Bound<'_, PyAny>,
    n: &Bound<'_, PyAny>,
    a: &Bound<'_, PyAny>,
    r: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
    t_gamma: Option<&Bound<'_, PyAny>>,
) -> PyResult<Bound<'py, PyDict>> {
    let model = model_from_python(model_id, gamma)?;
    let state = state_from_python(state)?;
    let times = times
        .extract::<PyReadonlyArray1<'_, f64>>()
        .map_err(|_| RF03InputError::new_err("times must be a contiguous float64 vector"))?;
    let times = times
        .as_slice()
        .map_err(|_| RF03InputError::new_err("times must be contiguous"))?;
    let contexts = context_history_from_python(sigma, n, a, r, q)?;
    validate_temperature_history(t_gamma, times.len())?;
    let result =
        integrate_context_history(model, state, times, &contexts).map_err(map_matter_error)?;
    integration_result_to_python(py, result)
}
