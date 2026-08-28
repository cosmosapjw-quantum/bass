//! Thin registration for the RF-01 classes and actionable exception types.

use pyo3::prelude::*;

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
