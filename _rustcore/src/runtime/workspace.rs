//! Plan-bound reusable workspace with fail-fast exclusive-use semantics.

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, MutexGuard};

use crate::core::buffer::FixtureBuffers;
use crate::core::counters::RuntimeCounters;
use crate::runtime::RuntimeError;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WorkspaceSnapshot {
    pub size: usize,
    pub capacities: [usize; 5],
    pub all_zero: bool,
    pub busy: bool,
    pub poisoned: bool,
}

#[derive(Debug)]
pub struct WorkspaceCore {
    plan_id: u64,
    plan_fingerprint: String,
    size: usize,
    busy: AtomicBool,
    poisoned: AtomicBool,
    buffers: Mutex<Option<FixtureBuffers>>,
}

pub struct WorkspaceLease<'a> {
    workspace: &'a WorkspaceCore,
}

impl Drop for WorkspaceLease<'_> {
    fn drop(&mut self) {
        self.workspace.busy.store(false, Ordering::Release);
    }
}

impl WorkspaceCore {
    pub fn new(
        plan_id: u64,
        plan_fingerprint: String,
        size: usize,
        counters: &RuntimeCounters,
    ) -> Result<Arc<Self>, RuntimeError> {
        let (buffers, observation) = FixtureBuffers::new(size)
            .map_err(|message| RuntimeError::InvalidConfig(message.to_owned()))?;
        counters.observe_workspace_sizing(observation.allocations);
        Ok(Arc::new(Self {
            plan_id,
            plan_fingerprint,
            size,
            busy: AtomicBool::new(false),
            poisoned: AtomicBool::new(false),
            buffers: Mutex::new(Some(buffers)),
        }))
    }

    pub fn plan_fingerprint(&self) -> &str {
        &self.plan_fingerprint
    }

    pub const fn size(&self) -> usize {
        self.size
    }

    pub fn is_busy(&self) -> bool {
        self.busy.load(Ordering::Acquire)
    }

    pub fn is_poisoned(&self) -> bool {
        self.poisoned.load(Ordering::Acquire)
    }

    pub fn validate_plan(&self, plan_id: u64) -> Result<(), RuntimeError> {
        if self.plan_id != plan_id {
            return Err(RuntimeError::PlanMismatch(
                "workspace belongs to a different RuntimePlan".to_owned(),
            ));
        }
        Ok(())
    }

    pub fn try_enter(&self, plan_id: u64) -> Result<WorkspaceLease<'_>, RuntimeError> {
        self.validate_plan(plan_id)?;
        if self.is_poisoned() {
            return Err(RuntimeError::WorkspaceState(
                "workspace is poisoned; call recover() explicitly before reuse".to_owned(),
            ));
        }
        self.busy
            .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
            .map_err(|_| RuntimeError::WorkspaceBusy("workspace is busy".to_owned()))?;
        Ok(WorkspaceLease { workspace: self })
    }

    fn slot(&self) -> Result<MutexGuard<'_, Option<FixtureBuffers>>, RuntimeError> {
        self.buffers.lock().map_err(|_| {
            self.poisoned.store(true, Ordering::Release);
            RuntimeError::WorkspaceState(
                "workspace buffer lock is poisoned; call recover() explicitly".to_owned(),
            )
        })
    }

    pub fn take_buffers(&self) -> Result<FixtureBuffers, RuntimeError> {
        self.slot()?.take().ok_or_else(|| {
            RuntimeError::WorkspaceState(
                "workspace buffers are unavailable or already in use".to_owned(),
            )
        })
    }

    pub fn return_buffers(&self, buffers: FixtureBuffers) -> Result<(), RuntimeError> {
        let mut slot = self.slot()?;
        if slot.is_some() {
            return Err(RuntimeError::WorkspaceState(
                "workspace buffer slot was unexpectedly occupied".to_owned(),
            ));
        }
        *slot = Some(buffers);
        Ok(())
    }

    pub fn poison_and_discard(&self) {
        self.poisoned.store(true, Ordering::Release);
        if let Ok(mut slot) = self.buffers.lock() {
            *slot = None;
        }
    }

    pub fn reset(&self) -> Result<(), RuntimeError> {
        let _lease = self.try_enter(self.plan_id)?;
        let mut slot = self.slot()?;
        let buffers = slot.as_mut().ok_or_else(|| {
            RuntimeError::WorkspaceState("workspace buffers are unavailable".to_owned())
        })?;
        buffers.reset();
        Ok(())
    }

    pub fn recover(&self, counters: &RuntimeCounters) -> Result<(), RuntimeError> {
        if self
            .busy
            .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
            .is_err()
        {
            return Err(RuntimeError::WorkspaceBusy("workspace is busy".to_owned()));
        }
        let lease = WorkspaceLease { workspace: self };
        let (buffers, observation) = FixtureBuffers::new(self.size)
            .map_err(|message| RuntimeError::WorkspaceState(message.to_owned()))?;
        counters.observe_workspace_sizing(observation.allocations);
        let mut slot = self
            .buffers
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        *slot = Some(buffers);
        self.buffers.clear_poison();
        self.poisoned.store(false, Ordering::Release);
        drop(slot);
        drop(lease);
        Ok(())
    }

    pub fn snapshot(&self) -> Result<WorkspaceSnapshot, RuntimeError> {
        let busy = self.is_busy();
        let poisoned = self.is_poisoned();
        let slot = self.slot()?;
        let (capacities, all_zero) = match slot.as_ref() {
            Some(buffers) => (buffers.capacities(), buffers.all_zero()),
            None => ([0; 5], false),
        };
        Ok(WorkspaceSnapshot {
            size: self.size,
            capacities,
            all_zero,
            busy,
            poisoned,
        })
    }
}
