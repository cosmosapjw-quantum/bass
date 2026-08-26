//! PyO3 adapter for the explicit, default-off generic-vector parity route.

use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyReadonlyArray1, PyReadonlyArray2, PyUntypedArrayMethods};
use pyo3::create_exception;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::kinetic::generic_vector::{
    execute, ActiveGenericVectorHost, GenericVectorHostDisposition, GenericVectorHostError,
};

create_exception!(
    bianchi_rustcore,
    GenericVectorHostDisabledError,
    PyRuntimeError
);
create_exception!(bianchi_rustcore, GenericVectorHostInputError, PyValueError);

fn map_error(error: GenericVectorHostError) -> PyErr {
    match error {
        GenericVectorHostError::Disabled => {
            GenericVectorHostDisabledError::new_err(error.to_string())
        }
        GenericVectorHostError::InvalidInput(_) => {
            GenericVectorHostInputError::new_err(error.to_string())
        }
    }
}

fn matrix_to_numpy<'py>(
    py: Python<'py>,
    matrix: &nalgebra::DMatrix<f64>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    Array2::from_shape_fn((matrix.nrows(), matrix.ncols()), |(row, column)| {
        matrix[(row, column)]
    })
    .into_pyarray(py)
}

fn vector_to_numpy<'py>(
    py: Python<'py>,
    vector: &nalgebra::DVector<f64>,
) -> Bound<'py, numpy::PyArray1<f64>> {
    Array1::from_iter(vector.iter().copied()).into_pyarray(py)
}

fn active_to_dict<'py>(
    py: Python<'py>,
    output: ActiveGenericVectorHost,
) -> PyResult<Bound<'py, PyDict>> {
    let result = PyDict::new(py);
    let node_count = output.e_normal.len();
    let state_size = output.equilibrium.len();
    result.set_item("schema", "bass.generic-vector-host/v1")?;
    result.set_item("route_default", "OFF")?;
    result.set_item("collision_off", false)?;
    result.set_item("vacuum_disposition", "ACTIVE_NONVACUUM")?;
    result.set_item("beta_quotiented", false)?;
    result.set_item("node_count", node_count)?;
    result.set_item("state_size", state_size)?;
    result.set_item("gamma", output.gamma)?;
    result.set_item("alpha", output.alpha)?;
    result.set_item("global_rate", output.global_rate)?;
    result.set_item(
        "e_normal",
        Array2::from_shape_fn((node_count, 3), |(node, component)| {
            output.e_normal[node][component]
        })
        .into_pyarray(py),
    )?;
    result.set_item(
        "w_normal",
        Array1::from_vec(output.w_normal).into_pyarray(py),
    )?;
    result.set_item("doppler", Array1::from_vec(output.doppler).into_pyarray(py))?;
    result.set_item(
        "direction_factor",
        Array1::from_vec(output.direction_factor).into_pyarray(py),
    )?;
    result.set_item(
        "node_rate",
        Array1::from_vec(output.node_rate).into_pyarray(py),
    )?;
    result.set_item("equilibrium", vector_to_numpy(py, &output.equilibrium))?;
    result.set_item(
        "equilibrium_dot",
        vector_to_numpy(py, &output.equilibrium_dot),
    )?;
    result.set_item(
        "normalized_left",
        vector_to_numpy(py, &output.normalized_left),
    )?;
    result.set_item(
        "normalized_left_dot",
        vector_to_numpy(py, &output.normalized_left_dot),
    )?;
    result.set_item("collision", matrix_to_numpy(py, &output.collision))?;
    result.set_item("projector", matrix_to_numpy(py, &output.projector))?;
    result.set_item("projector_dot", matrix_to_numpy(py, &output.projector_dot))?;
    result.set_item("kato", matrix_to_numpy(py, &output.kato))?;
    Ok(result)
}

fn vacuum_to_dict<'py>(py: Python<'py>, state_size: usize) -> PyResult<Bound<'py, PyDict>> {
    let result = PyDict::new(py);
    result.set_item("schema", "bass.generic-vector-host/v1")?;
    result.set_item("route_default", "OFF")?;
    result.set_item("collision_off", true)?;
    result.set_item(
        "vacuum_disposition",
        "COLLISION_OFF_NO_NONTRIVIAL_PROJECTOR",
    )?;
    result.set_item("beta_quotiented", true)?;
    result.set_item("node_count", state_size / 9)?;
    result.set_item("state_size", state_size)?;
    result.set_item("gamma", py.None())?;
    result.set_item("alpha", 0.0)?;
    result.set_item("global_rate", 0.0)?;
    result.set_item("e_normal", py.None())?;
    result.set_item("w_normal", py.None())?;
    result.set_item("doppler", py.None())?;
    result.set_item("direction_factor", py.None())?;
    result.set_item(
        "node_rate",
        Array1::<f64>::zeros(state_size / 9).into_pyarray(py),
    )?;
    result.set_item("equilibrium", py.None())?;
    result.set_item("equilibrium_dot", py.None())?;
    result.set_item("normalized_left", py.None())?;
    result.set_item("normalized_left_dot", py.None())?;
    result.set_item(
        "collision",
        Array2::<f64>::zeros((state_size, state_size)).into_pyarray(py),
    )?;
    result.set_item("projector", py.None())?;
    result.set_item("projector_dot", py.None())?;
    result.set_item("kato", py.None())?;
    Ok(result)
}

#[pyfunction]
#[pyo3(signature = (e_rest, w_rest, beta, beta_dot, alpha, *, enabled = false))]
fn generic_vector_host<'py>(
    py: Python<'py>,
    e_rest: PyReadonlyArray2<'py, f64>,
    w_rest: PyReadonlyArray1<'py, f64>,
    beta: PyReadonlyArray1<'py, f64>,
    beta_dot: PyReadonlyArray1<'py, f64>,
    alpha: f64,
    enabled: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let direction_shape = e_rest.shape();
    if direction_shape.len() != 2 || direction_shape[1] != 3 {
        return Err(GenericVectorHostInputError::new_err(
            "e_rest must be a C-contiguous float64 array with shape (N,3)",
        ));
    }
    let direction_values = e_rest.as_slice().map_err(|_| {
        GenericVectorHostInputError::new_err(
            "e_rest must be a C-contiguous float64 array with shape (N,3)",
        )
    })?;
    let weights = w_rest
        .as_slice()
        .map_err(|_| GenericVectorHostInputError::new_err("w_rest must be C-contiguous float64"))?;
    let beta_values = beta
        .as_slice()
        .map_err(|_| GenericVectorHostInputError::new_err("beta must be C-contiguous float64"))?;
    let beta_dot_values = beta_dot.as_slice().map_err(|_| {
        GenericVectorHostInputError::new_err("beta_dot must be C-contiguous float64")
    })?;
    if beta_values.len() != 3 || beta_dot_values.len() != 3 {
        return Err(GenericVectorHostInputError::new_err(
            "beta and beta_dot must each have length 3",
        ));
    }
    let directions: Vec<[f64; 3]> = direction_values
        .chunks_exact(3)
        .map(|row| [row[0], row[1], row[2]])
        .collect();
    let weights = weights.to_vec();
    let beta = [beta_values[0], beta_values[1], beta_values[2]];
    let beta_dot = [beta_dot_values[0], beta_dot_values[1], beta_dot_values[2]];

    let disposition = py
        .detach(move || execute(&directions, &weights, beta, beta_dot, alpha, enabled))
        .map_err(map_error)?;
    match disposition {
        GenericVectorHostDisposition::Active(output) => active_to_dict(py, *output),
        GenericVectorHostDisposition::CollisionOff { state_size } => vacuum_to_dict(py, state_size),
    }
}

pub fn register_generic_vector(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add(
        "GenericVectorHostDisabledError",
        py.get_type::<GenericVectorHostDisabledError>(),
    )?;
    module.add(
        "GenericVectorHostInputError",
        py.get_type::<GenericVectorHostInputError>(),
    )?;
    module.add_function(wrap_pyfunction!(generic_vector_host, module)?)?;
    Ok(())
}
