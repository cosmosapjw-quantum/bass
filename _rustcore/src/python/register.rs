//! Thin registration for the RF-01 classes and actionable exception types.

use pyo3::prelude::*;

use super::background::{
    chart_aux, chart_constraints, chart_jvp, chart_project, chart_project_checked, chart_rhs,
    integrate_background, integrate_background_batch_history, integrate_background_history,
    integrate_background_whiplash, integrate_batch, restart_background_history,
    scalar_chart_schema,
};
use super::geometry::{
    qg_classify, qg_curvature, qg_geometry_identity, qg_jacobi, qg_kappa, qg_ricci3,
    qg_structure_constants, rf02c_execution_identity,
};
use super::rf03_matter::{
    rf03_matter_force, rf03_matter_force_jvp, rf03_matter_integrate, rf03_matter_integrate_history,
    RF03DomainError, RF03InputError, RF03ModelError,
};
use super::rf03_tilt::{rf03_tilt_invariants, th_force_and_matrix, th_integrate, th_rhs};

use super::runtime::{
    InvalidBufferError, PlanMismatchError, PoolConstructionError, PyRuntimePlan, PyWorkspace,
    RuntimeConfigError, RuntimePanicError, UnsupportedCapabilityError, WorkspaceBusyError,
    WorkspaceStateError,
};

pub fn register_runtime(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add("RuntimeConfigError", py.get_type::<RuntimeConfigError>())?;
    module.add("InvalidBufferError", py.get_type::<InvalidBufferError>())?;
    module.add("PlanMismatchError", py.get_type::<PlanMismatchError>())?;
    module.add("WorkspaceBusyError", py.get_type::<WorkspaceBusyError>())?;
    module.add("WorkspaceStateError", py.get_type::<WorkspaceStateError>())?;
    module.add(
        "UnsupportedCapabilityError",
        py.get_type::<UnsupportedCapabilityError>(),
    )?;
    module.add(
        "PoolConstructionError",
        py.get_type::<PoolConstructionError>(),
    )?;
    module.add("RuntimePanicError", py.get_type::<RuntimePanicError>())?;
    module.add_class::<PyRuntimePlan>()?;
    module.add_class::<PyWorkspace>()?;
    Ok(())
}

pub fn register_geometry(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(qg_classify, module)?)?;
    module.add_function(wrap_pyfunction!(qg_jacobi, module)?)?;
    module.add_function(wrap_pyfunction!(qg_structure_constants, module)?)?;
    module.add_function(wrap_pyfunction!(qg_ricci3, module)?)?;
    module.add_function(wrap_pyfunction!(qg_curvature, module)?)?;
    module.add_function(wrap_pyfunction!(qg_kappa, module)?)?;
    module.add_function(wrap_pyfunction!(rf02c_execution_identity, module)?)?;
    module.add_function(wrap_pyfunction!(qg_geometry_identity, module)?)?;
    Ok(())
}

pub fn register_background(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(chart_rhs, module)?)?;
    module.add_function(wrap_pyfunction!(chart_aux, module)?)?;
    module.add_function(wrap_pyfunction!(scalar_chart_schema, module)?)?;
    module.add_function(wrap_pyfunction!(chart_jvp, module)?)?;
    module.add_function(wrap_pyfunction!(chart_constraints, module)?)?;
    module.add_function(wrap_pyfunction!(chart_project, module)?)?;
    module.add_function(wrap_pyfunction!(chart_project_checked, module)?)?;
    module.add_function(wrap_pyfunction!(integrate_background, module)?)?;
    module.add_function(wrap_pyfunction!(integrate_background_whiplash, module)?)?;
    module.add_function(wrap_pyfunction!(integrate_batch, module)?)?;
    module.add_function(wrap_pyfunction!(integrate_background_history, module)?)?;
    module.add_function(wrap_pyfunction!(restart_background_history, module)?)?;
    module.add_function(wrap_pyfunction!(
        integrate_background_batch_history,
        module
    )?)?;
    Ok(())
}

pub fn register_rf03(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add("RF03ModelError", py.get_type::<RF03ModelError>())?;
    module.add("RF03DomainError", py.get_type::<RF03DomainError>())?;
    module.add("RF03InputError", py.get_type::<RF03InputError>())?;
    module.add_function(wrap_pyfunction!(rf03_matter_force, module)?)?;
    module.add_function(wrap_pyfunction!(rf03_matter_force_jvp, module)?)?;
    module.add_function(wrap_pyfunction!(rf03_matter_integrate, module)?)?;
    module.add_function(wrap_pyfunction!(rf03_matter_integrate_history, module)?)?;
    module.add_function(wrap_pyfunction!(rf03_tilt_invariants, module)?)?;
    module.add_function(wrap_pyfunction!(th_integrate, module)?)?;
    module.add_function(wrap_pyfunction!(th_rhs, module)?)?;
    module.add_function(wrap_pyfunction!(th_force_and_matrix, module)?)?;
    Ok(())
}
