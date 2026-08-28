//! Thin PyO3 adapters for RF-03 finite-boost invariants and inherited closure routes.

use numpy::ndarray::{Array1, Array2};
use numpy::{IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

use crate::kinetic;
use crate::matter::MatterState;
use crate::tilt::tilt_invariants;

use super::rf03_matter::{map_matter_error, scalar_from_python, vector_from_python};

type Array1Pair<'py> = (Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>);

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

// Inherited R5b tilted hierarchy adapters.  Their numerical owners remain
// `kinetic::tilted_hier`; RF-03 only relocates this Python boundary out of the
// crate root so `lib.rs` remains registration wiring.
const TH_GEO_LEN: usize = 142;

fn th_geo(row: &[f64]) -> PyResult<kinetic::tilted_hier::HGeo> {
    if row.len() != TH_GEO_LEN {
        return Err(PyValueError::new_err(format!(
            "geo row must be {TH_GEO_LEN} long, got {}",
            row.len()
        )));
    }
    let mut geometry = kinetic::tilted_terms::Geo {
        eup: [0.0; 12],
        edn: [0.0; 12],
        deup: [0.0; 12],
        hmix: [0.0; 16],
        uup: [0.0; 4],
        gam: [0.0; 64],
    };
    geometry.eup.copy_from_slice(&row[0..12]);
    geometry.edn.copy_from_slice(&row[12..24]);
    geometry.deup.copy_from_slice(&row[24..36]);
    geometry.hmix.copy_from_slice(&row[36..52]);
    geometry.uup.copy_from_slice(&row[52..56]);
    geometry.gam.copy_from_slice(&row[56..120]);
    let mut hierarchy_geometry = kinetic::tilted_hier::HGeo {
        base: geometry,
        h: row[120],
        sigma: [0.0; 9],
        omega: [0.0; 9],
        udot: [0.0; 3],
        gamma: 1.0,
        v: [0.0; 3],
    };
    hierarchy_geometry.sigma.copy_from_slice(&row[121..130]);
    hierarchy_geometry.omega.copy_from_slice(&row[130..139]);
    hierarchy_geometry.udot.copy_from_slice(&row[139..142]);
    Ok(hierarchy_geometry.finish())
}

fn th_geos(geos: &PyReadonlyArray2<f64>) -> PyResult<Vec<kinetic::tilted_hier::HGeo>> {
    let array = geos.as_array();
    if array.shape()[1] != TH_GEO_LEN {
        return Err(PyValueError::new_err(format!(
            "geo rows must be {TH_GEO_LEN} long, got {}",
            array.shape()[1]
        )));
    }
    (0..array.shape()[0])
        .map(|sample| {
            let row: Vec<f64> = (0..TH_GEO_LEN)
                .map(|component| array[[sample, component]])
                .collect();
            th_geo(&row)
        })
        .collect()
}

fn th_closure(
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<kinetic::tilted_hier::Closure> {
    let mode = kinetic::tilted_hier::Mode::from_code(mode_code)
        .ok_or_else(|| PyValueError::new_err(format!("unknown mode code {mode_code}")))?;
    Ok(kinetic::tilted_hier::Closure {
        mode,
        jdot,
        n_star: if n_star < 0 { None } else { Some(n_star) },
    })
}

fn th_signs(signs: &PyReadonlyArray1<f64>) -> PyResult<kinetic::tilted_hier::Signs> {
    let values = signs.as_slice()?;
    if values.len() != 8 {
        return Err(PyValueError::new_err(
            "signs must be [A, B, C, D, E, Omega, divcon, divfree]",
        ));
    }
    Ok(kinetic::tilted_hier::Signs {
        a: values[0],
        b: values[1],
        c: values[2],
        d: values[3],
        e: values[4],
        omega: values[5],
        divcon: values[6],
        divfree: values[7],
    })
}

fn th_mats(values: &[PyReadonlyArray1<f64>]) -> PyResult<Vec<Vec<f64>>> {
    values
        .iter()
        .map(|value| Ok(value.as_slice()?.to_vec()))
        .collect()
}

fn th_check(operators: &[Vec<f64>], bases: &[Vec<f64>], l_max: usize) -> PyResult<()> {
    if operators.len() < l_max + 1 || bases.len() < l_max + 1 {
        return Err(PyValueError::new_err(format!(
            "ops/bases must have l_max+1 = {} entries (got {}, {})",
            l_max + 1,
            operators.len(),
            bases.len()
        )));
    }
    for rank in 0..=l_max {
        let dimension = 3usize.pow(rank as u32);
        if rank >= 2 && operators[rank].len() != dimension * dimension {
            return Err(PyValueError::new_err(format!(
                "ops[{rank}] must be flat ({dimension},{dimension}), got {}",
                operators[rank].len()
            )));
        }
        if bases[rank].len() != dimension * (2 * rank + 1) {
            return Err(PyValueError::new_err(format!(
                "bases[{rank}] must be flat ({dimension},{}), got {}",
                2 * rank + 1,
                bases[rank].len()
            )));
        }
    }
    Ok(())
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub(crate) fn th_integrate<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geos: PyReadonlyArray2<f64>,
    nsteps: usize,
    dt: f64,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let closure = th_closure(mode_code, jdot, n_star)?;
    let state_len = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    let flat = j0.as_slice()?;
    if flat.len() != state_len {
        return Err(PyValueError::new_err(format!(
            "j0 must be {state_len} long"
        )));
    }
    let geometries = th_geos(&geos)?;
    if geometries.len() != 3 * nsteps {
        return Err(PyValueError::new_err("geos must hold 3 rows per step"));
    }
    let (signs, operators, bases) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&operators, &bases, l_max)?;
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, flat);
    let history = py.detach(|| {
        kinetic::tilted_hier::integrate(
            &grid,
            &geometries,
            nsteps,
            dt,
            &signs,
            &operators,
            &bases,
            closure,
        )
    });
    Ok(Array2::from_shape_vec((nsteps + 1, state_len), history)
        .map_err(|error| PyValueError::new_err(error.to_string()))?
        .into_pyarray(py))
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub(crate) fn th_rhs<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geo: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let closure = th_closure(mode_code, jdot, n_star)?;
    let (signs, operators, bases) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&operators, &bases, l_max)?;
    let geometry = th_geo(geo.as_slice()?)?;
    let state_len = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    if j0.as_slice()?.len() != state_len {
        return Err(PyValueError::new_err(format!(
            "j0 must be {state_len} long"
        )));
    }
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, j0.as_slice()?);
    let observed = py.detach(|| {
        kinetic::tilted_hier::rhs(&grid, &geometry, &signs, &operators, &bases, closure)
    });
    let mut flat = Vec::new();
    observed.flatten_state(&mut flat);
    Ok(Array1::from_vec(flat).into_pyarray(py))
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub(crate) fn th_force_and_matrix<'py>(
    py: Python<'py>,
    j0: PyReadonlyArray1<f64>,
    geo: PyReadonlyArray1<f64>,
    signs: PyReadonlyArray1<f64>,
    ops: Vec<PyReadonlyArray1<f64>>,
    bases: Vec<PyReadonlyArray1<f64>>,
    l_max: usize,
    i_max: usize,
    mode_code: usize,
    jdot: bool,
    n_star: i32,
) -> PyResult<Array1Pair<'py>> {
    let closure = th_closure(mode_code, jdot, n_star)?;
    let (signs, operators, bases) = (th_signs(&signs)?, th_mats(&ops)?, th_mats(&bases)?);
    th_check(&operators, &bases, l_max)?;
    let geometry = th_geo(geo.as_slice()?)?;
    let state_len = kinetic::tilted_hier::Grid::state_len(l_max, i_max);
    if j0.as_slice()?.len() != state_len {
        return Err(PyValueError::new_err(format!(
            "j0 must be {state_len} long"
        )));
    }
    let grid = kinetic::tilted_hier::Grid::from_state(l_max, i_max, j0.as_slice()?);
    let (force, matrix) = py.detach(|| {
        kinetic::tilted_hier::force_and_matrix(
            &grid, &geometry, &signs, &operators, &bases, closure,
        )
    });
    Ok((
        Array1::from_vec(force).into_pyarray(py),
        Array1::from_vec(matrix).into_pyarray(py),
    ))
}
