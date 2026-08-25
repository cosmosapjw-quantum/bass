//! Thin PyO3 adapter for RuntimePlan and Workspace.

use std::sync::Arc;

use numpy::{IntoPyArray, PyArray1, PyArrayDescrMethods, PyArrayMethods, PyUntypedArrayMethods};
use pyo3::create_exception;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

use crate::core::counters::CounterSnapshot;
use crate::core::policy::DEFAULT_FIXTURE_SIZE;
use crate::runtime::plan::RuntimePlanCore;
use crate::runtime::workspace::{WorkspaceCore, WorkspaceSnapshot};
use crate::runtime::RuntimeError;

create_exception!(bianchi_rustcore, RuntimeConfigError, PyValueError);
create_exception!(bianchi_rustcore, InvalidBufferError, PyValueError);
create_exception!(bianchi_rustcore, PlanMismatchError, PyRuntimeError);
create_exception!(bianchi_rustcore, WorkspaceBusyError, PyRuntimeError);
create_exception!(bianchi_rustcore, WorkspaceStateError, PyRuntimeError);
create_exception!(bianchi_rustcore, UnsupportedCapabilityError, PyRuntimeError);
create_exception!(bianchi_rustcore, PoolConstructionError, PyRuntimeError);
create_exception!(bianchi_rustcore, RuntimePanicError, PyRuntimeError);

pub fn map_runtime_error(error: RuntimeError) -> PyErr {
    match error {
        RuntimeError::InvalidConfig(message) => RuntimeConfigError::new_err(message),
        RuntimeError::InvalidBuffer(message) => InvalidBufferError::new_err(message),
        RuntimeError::PlanMismatch(message) => PlanMismatchError::new_err(message),
        RuntimeError::WorkspaceBusy(message) => WorkspaceBusyError::new_err(message),
        RuntimeError::WorkspaceState(message) => WorkspaceStateError::new_err(message),
        RuntimeError::UnsupportedCapability(message) => {
            UnsupportedCapabilityError::new_err(message)
        }
        RuntimeError::PoolConstruction(message) => PoolConstructionError::new_err(message),
        RuntimeError::ContainedPanic(message) => RuntimePanicError::new_err(message),
    }
}

fn counters_to_dict<'py>(
    py: Python<'py>,
    counters: CounterSnapshot,
) -> PyResult<Bound<'py, PyDict>> {
    let result = PyDict::new(py);
    result.set_item("ffi_compute_entries", counters.ffi_compute_entries)?;
    result.set_item("input_copies", counters.input_copies)?;
    result.set_item("output_copies", counters.output_copies)?;
    result.set_item("workspace_growth_events", counters.workspace_growth_events)?;
    result.set_item(
        "designated_rust_allocations",
        counters.designated_rust_allocations,
    )?;
    Ok(result)
}

fn workspace_snapshot_to_dict<'py>(
    py: Python<'py>,
    snapshot: WorkspaceSnapshot,
) -> PyResult<Bound<'py, PyDict>> {
    let result = PyDict::new(py);
    result.set_item("size", snapshot.size)?;
    result.set_item("capacities", snapshot.capacities.to_vec())?;
    result.set_item("all_zero", snapshot.all_zero)?;
    result.set_item("busy", snapshot.busy)?;
    result.set_item("poisoned", snapshot.poisoned)?;
    Ok(result)
}

#[pyclass(name = "RuntimePlan", frozen, module = "bianchi_rustcore")]
pub struct PyRuntimePlan {
    inner: Arc<RuntimePlanCore>,
}

#[pyclass(name = "Workspace", frozen, module = "bianchi_rustcore")]
pub struct PyWorkspace {
    inner: Arc<WorkspaceCore>,
    plan: Arc<RuntimePlanCore>,
}

#[pymethods]
impl PyRuntimePlan {
    #[new]
    #[pyo3(signature = (thread_count, *, fixture_size = DEFAULT_FIXTURE_SIZE, require_finite = true, cpu_variant = "scalar"))]
    fn new(
        thread_count: i64,
        fixture_size: u64,
        require_finite: bool,
        cpu_variant: &str,
    ) -> PyResult<Self> {
        Ok(Self {
            inner: RuntimePlanCore::from_raw(
                thread_count,
                fixture_size,
                require_finite,
                cpu_variant,
            )
            .map_err(map_runtime_error)?,
        })
    }

    #[getter]
    fn thread_count(&self) -> usize {
        self.inner.config().thread_count
    }

    #[getter]
    fn private_pool_size(&self) -> usize {
        self.inner.private_pool_size()
    }

    #[getter]
    fn fixture_size(&self) -> usize {
        self.inner.config().fixture_size
    }

    #[getter]
    fn cpu_variant(&self) -> &'static str {
        self.inner.config().cpu_variant.as_str()
    }

    #[getter]
    fn fingerprint(&self) -> &str {
        self.inner.fingerprint()
    }

    fn capability_receipt<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let receipt = PyDict::new(py);
        receipt.set_item("schema", "bass-runtime-plan-capability-v1")?;
        receipt.set_item("fingerprint", self.inner.fingerprint())?;
        receipt.set_item("thread_count", self.inner.config().thread_count)?;
        receipt.set_item("private_pool_size", self.inner.private_pool_size())?;
        receipt.set_item("private_rayon_pool", true)?;
        receipt.set_item("uses_global_rayon_pool", false)?;
        receipt.set_item("cpu_variant", self.inner.config().cpu_variant.as_str())?;
        receipt.set_item("require_finite", self.inner.config().require_finite)?;
        receipt.set_item("fixture_size", self.inner.config().fixture_size)?;
        receipt.set_item("immutable_table_id", "rf01-synthetic-v1")?;
        receipt.set_item(
            "build_profile",
            if cfg!(debug_assertions) {
                "debug"
            } else {
                "release"
            },
        )?;
        Ok(receipt)
    }

    fn counters<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        counters_to_dict(py, self.inner.counters())
    }

    fn reset_counters(&self) {
        self.inner.reset_counters();
    }

    fn workspace(&self) -> PyResult<PyWorkspace> {
        Ok(PyWorkspace {
            inner: self.inner.workspace().map_err(map_runtime_error)?,
            plan: Arc::clone(&self.inner),
        })
    }

    #[pyo3(signature = (values, workspace, *, steps = 1))]
    fn run_fixture<'py>(
        &self,
        py: Python<'py>,
        values: &Bound<'py, PyAny>,
        workspace: PyRef<'py, PyWorkspace>,
        steps: u64,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        workspace
            .inner
            .validate_plan(self.inner.id())
            .map_err(map_runtime_error)?;
        let array = values.cast::<PyArray1<f64>>().map_err(|_| {
            InvalidBufferError::new_err("expected a rank-1 native-endian float64 NumPy array")
        })?;
        if array.dtype().is_native_byteorder() != Some(true) {
            return Err(InvalidBufferError::new_err(
                "input must use native-endian float64 storage",
            ));
        }
        if !array.is_c_contiguous() || !array.is_aligned() {
            return Err(InvalidBufferError::new_err(
                "input must be aligned and C-contiguous",
            ));
        }
        if array.len() != self.inner.config().fixture_size {
            return Err(InvalidBufferError::new_err(format!(
                "input length {} does not match fixture length {}",
                array.len(),
                self.inner.config().fixture_size
            )));
        }
        let readonly = array.readonly();
        let borrowed = readonly.as_slice().map_err(|_| {
            InvalidBufferError::new_err("input cannot be borrowed as contiguous float64")
        })?;
        self.inner
            .validate_input(borrowed)
            .map_err(map_runtime_error)?;
        let owned = borrowed.to_vec();
        self.inner.observe_input_copy();
        drop(readonly);

        let plan = Arc::clone(&self.inner);
        let workspace = Arc::clone(&workspace.inner);
        let output = py
            .detach(move || plan.run_fixture(&workspace, &owned, steps))
            .map_err(map_runtime_error)?;
        Ok(output.into_pyarray(py))
    }

    fn _test_recursive_reentry(&self, workspace: PyRef<'_, PyWorkspace>) -> PyResult<()> {
        self.inner
            .test_recursive_reentry(&workspace.inner)
            .map_err(map_runtime_error)
    }

    fn _test_panic(&self, py: Python<'_>, workspace: PyRef<'_, PyWorkspace>) -> PyResult<()> {
        let plan = Arc::clone(&self.inner);
        let workspace = Arc::clone(&workspace.inner);
        py.detach(move || plan.test_contained_panic(&workspace))
            .map_err(map_runtime_error)
    }

    fn __repr__(&self) -> String {
        format!(
            "RuntimePlan(thread_count={}, fixture_size={}, cpu_variant='{}')",
            self.inner.config().thread_count,
            self.inner.config().fixture_size,
            self.inner.config().cpu_variant.as_str(),
        )
    }
}

#[pymethods]
impl PyWorkspace {
    #[getter]
    fn plan_fingerprint(&self) -> &str {
        self.inner.plan_fingerprint()
    }

    #[getter]
    fn size(&self) -> usize {
        self.inner.size()
    }

    #[getter]
    fn is_busy(&self) -> bool {
        self.inner.is_busy()
    }

    #[getter]
    fn is_poisoned(&self) -> bool {
        self.inner.is_poisoned()
    }

    fn snapshot<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        workspace_snapshot_to_dict(py, self.inner.snapshot().map_err(map_runtime_error)?)
    }

    fn reset(&self) -> PyResult<()> {
        self.inner.reset().map_err(map_runtime_error)
    }

    fn recover(&self) -> PyResult<()> {
        self.plan
            .recover_workspace(&self.inner)
            .map_err(map_runtime_error)
    }

    fn __repr__(&self) -> String {
        format!(
            "Workspace(size={}, plan_fingerprint='{}')",
            self.inner.size(),
            self.inner.plan_fingerprint(),
        )
    }
}
