//! Immutable shareable RuntimePlan with one private Rayon pool.

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use rayon::{ThreadPool, ThreadPoolBuilder};

use crate::core::counters::{CounterSnapshot, RuntimeCounters};
use crate::core::policy::{PlanConfig, PolicyError};
use crate::runtime::workspace::WorkspaceCore;
use crate::runtime::RuntimeError;

static NEXT_PLAN_ID: AtomicU64 = AtomicU64::new(1);

#[derive(Debug)]
pub struct RuntimePlanCore {
    id: u64,
    config: PlanConfig,
    fingerprint: String,
    pool: ThreadPool,
    table: [f64; 4],
    counters: RuntimeCounters,
}

impl RuntimePlanCore {
    pub fn new(config: PlanConfig) -> Result<Arc<Self>, RuntimeError> {
        let fingerprint = config.canonical_fingerprint();
        let pool = ThreadPoolBuilder::new()
            .num_threads(config.thread_count)
            .thread_name({
                let fingerprint = fingerprint.clone();
                move |index| format!("bass-{fingerprint}-{index}")
            })
            .build()
            .map_err(|error| {
                RuntimeError::PoolConstruction(format!(
                    "private Rayon pool construction failed: {error}"
                ))
            })?;
        Ok(Arc::new(Self {
            id: NEXT_PLAN_ID.fetch_add(1, Ordering::Relaxed),
            config,
            fingerprint,
            pool,
            table: [0.5, 0.25, 0.125, 0.0625],
            counters: RuntimeCounters::default(),
        }))
    }

    pub fn from_raw(
        thread_count: i64,
        fixture_size: u64,
        require_finite: bool,
        cpu_variant: &str,
    ) -> Result<Arc<Self>, RuntimeError> {
        let config = PlanConfig::validate(thread_count, fixture_size, require_finite, cpu_variant)
            .map_err(|error| match error {
                PolicyError::UnsupportedCpuVariant(_) => {
                    RuntimeError::UnsupportedCapability(error.to_string())
                }
                _ => RuntimeError::InvalidConfig(error.to_string()),
            })?;
        Self::new(config)
    }

    pub const fn id(&self) -> u64 {
        self.id
    }

    pub fn config(&self) -> &PlanConfig {
        &self.config
    }

    pub fn fingerprint(&self) -> &str {
        &self.fingerprint
    }

    pub fn private_pool_size(&self) -> usize {
        self.pool.current_num_threads()
    }

    pub fn counters(&self) -> CounterSnapshot {
        self.counters.snapshot()
    }

    pub fn reset_counters(&self) {
        self.counters.reset();
    }

    pub fn observe_input_copy(&self) {
        self.counters.observe_input_copy();
    }

    pub fn workspace(self: &Arc<Self>) -> Result<Arc<WorkspaceCore>, RuntimeError> {
        WorkspaceCore::new(
            self.id,
            self.fingerprint.clone(),
            self.config.fixture_size,
            &self.counters,
        )
    }

    pub fn recover_workspace(&self, workspace: &WorkspaceCore) -> Result<(), RuntimeError> {
        workspace.validate_plan(self.id)?;
        workspace.recover(&self.counters)
    }

    pub fn validate_input(&self, input: &[f64]) -> Result<(), RuntimeError> {
        if input.len() != self.config.fixture_size {
            return Err(RuntimeError::InvalidBuffer(format!(
                "input length {} does not match fixture length {}",
                input.len(),
                self.config.fixture_size
            )));
        }
        if self.config.require_finite && input.iter().any(|value| !value.is_finite()) {
            return Err(RuntimeError::InvalidBuffer(
                "input violates the declared finite-value policy".to_owned(),
            ));
        }
        Ok(())
    }

    fn checked_steps(steps: u64) -> Result<usize, RuntimeError> {
        if steps == 0 {
            return Err(RuntimeError::InvalidBuffer(
                "steps must be a positive integer".to_owned(),
            ));
        }
        usize::try_from(steps)
            .map_err(|_| RuntimeError::InvalidBuffer("steps exceeds this host ABI".to_owned()))
    }

    pub fn run_fixture(
        &self,
        workspace: &WorkspaceCore,
        input: &[f64],
        steps: u64,
    ) -> Result<Vec<f64>, RuntimeError> {
        self.validate_input(input)?;
        let steps = Self::checked_steps(steps)?;
        let _lease = workspace.try_enter(self.id)?;
        let mut buffers = workspace.take_buffers()?;
        if buffers.size() != self.config.fixture_size {
            workspace.poison_and_discard();
            return Err(RuntimeError::WorkspaceState(
                "workspace size does not match its RuntimePlan".to_owned(),
            ));
        }
        self.counters.observe_compute_entry();
        let result = catch_unwind(AssertUnwindSafe(|| {
            self.pool.install(|| {
                buffers.load_input(input).expect("validated input length");
                self.counters.observe_input_copy();
                buffers.run_designated_fixture(steps, &self.table);
                let output = buffers.owned_output();
                self.counters.observe_output_copy();
                output
            })
        }));
        match result {
            Ok(output) => {
                workspace.return_buffers(buffers)?;
                Ok(output)
            }
            Err(_) => {
                workspace.poison_and_discard();
                Err(RuntimeError::ContainedPanic(
                    "contained Rust panic in RuntimePlan computation; workspace poisoned"
                        .to_owned(),
                ))
            }
        }
    }

    pub fn test_recursive_reentry(&self, workspace: &WorkspaceCore) -> Result<(), RuntimeError> {
        let _lease = workspace.try_enter(self.id)?;
        match workspace.try_enter(self.id) {
            Err(RuntimeError::WorkspaceBusy(_)) => Err(RuntimeError::WorkspaceBusy(
                "reentrant workspace reuse is busy".to_owned(),
            )),
            Err(error) => Err(error),
            Ok(_) => Err(RuntimeError::WorkspaceState(
                "recursive workspace acquisition unexpectedly succeeded".to_owned(),
            )),
        }
    }

    pub fn test_contained_panic(&self, workspace: &WorkspaceCore) -> Result<(), RuntimeError> {
        let _lease = workspace.try_enter(self.id)?;
        let buffers = workspace.take_buffers()?;
        self.counters.observe_compute_entry();
        let caught = catch_unwind(AssertUnwindSafe(|| {
            self.pool
                .install(|| panic!("RF-01 contained panic fixture"));
        }));
        match caught {
            Ok(()) => {
                workspace.return_buffers(buffers)?;
                Err(RuntimeError::WorkspaceState(
                    "panic fixture unexpectedly returned".to_owned(),
                ))
            }
            Err(_) => {
                drop(buffers);
                workspace.poison_and_discard();
                Err(RuntimeError::ContainedPanic(
                    "contained Rust panic in RuntimePlan computation; workspace poisoned"
                        .to_owned(),
                ))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::buffer::FixtureBuffers;
    use crate::core::counters::{observations, reset, set_thread_tracking};

    fn plan(threads: i64, size: u64) -> Arc<RuntimePlanCore> {
        RuntimePlanCore::from_raw(threads, size, true, "scalar").unwrap()
    }

    #[test]
    fn private_pools_coexist_and_fingerprints_are_stable() {
        let one = plan(1, 64);
        let two = plan(2, 64);
        let two_again = plan(2, 64);
        assert_eq!(one.private_pool_size(), 1);
        assert_eq!(two.private_pool_size(), 2);
        assert_ne!(one.fingerprint(), two.fingerprint());
        assert_eq!(two.fingerprint(), two_again.fingerprint());
    }

    #[test]
    fn recursive_and_cross_plan_workspace_use_fail_closed() {
        let one = plan(1, 8);
        let two = plan(2, 8);
        let workspace = one.workspace().unwrap();
        assert!(matches!(
            one.test_recursive_reentry(&workspace),
            Err(RuntimeError::WorkspaceBusy(_))
        ));
        assert!(matches!(
            two.run_fixture(&workspace, &[0.0; 8], 1),
            Err(RuntimeError::PlanMismatch(_))
        ));
    }

    #[test]
    fn sized_workspace_has_no_designated_growth_for_one_hundred_steps() {
        let plan = plan(2, 128);
        let workspace = plan.workspace().unwrap();
        plan.run_fixture(&workspace, &[0.25; 128], 1).unwrap();
        plan.reset_counters();
        plan.run_fixture(&workspace, &[0.25; 128], 100).unwrap();
        assert_eq!(
            plan.counters(),
            CounterSnapshot {
                ffi_compute_entries: 1,
                input_copies: 1,
                output_copies: 1,
                workspace_growth_events: 0,
                designated_rust_allocations: 0,
            }
        );
    }

    #[test]
    fn designated_inner_loop_has_zero_test_allocator_observations_after_sizing() {
        let plan = plan(2, 128);
        let (mut buffers, _) = FixtureBuffers::new(128).unwrap();
        buffers.load_input(&[0.25; 128]).unwrap();
        plan.pool.broadcast(|_| set_thread_tracking(true));
        reset();
        plan.pool
            .install(|| buffers.run_designated_fixture(100, &plan.table));
        let inner_allocations = observations();
        plan.pool.broadcast(|_| set_thread_tracking(false));
        assert_eq!(inner_allocations, 0);
    }
}
