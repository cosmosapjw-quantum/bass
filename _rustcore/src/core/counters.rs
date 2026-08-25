//! Per-plan monotonic counters for the RF-01 runtime boundary.

use std::sync::atomic::{AtomicU64, Ordering};

#[cfg(test)]
mod allocation_probe {
    use std::alloc::{GlobalAlloc, Layout, System};
    use std::cell::Cell;
    use std::sync::atomic::{AtomicU64, Ordering};

    thread_local! {
        static TRACK_THIS_THREAD: Cell<bool> = const { Cell::new(false) };
    }

    static OBSERVATIONS: AtomicU64 = AtomicU64::new(0);

    pub struct TestAllocator;

    #[global_allocator]
    static ALLOCATOR: TestAllocator = TestAllocator;

    fn observe() {
        TRACK_THIS_THREAD.with(|tracking| {
            if tracking.get() {
                OBSERVATIONS.fetch_add(1, Ordering::Relaxed);
            }
        });
    }

    unsafe impl GlobalAlloc for TestAllocator {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            observe();
            unsafe { System.alloc(layout) }
        }

        unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
            observe();
            unsafe { System.alloc_zeroed(layout) }
        }

        unsafe fn dealloc(&self, pointer: *mut u8, layout: Layout) {
            unsafe { System.dealloc(pointer, layout) }
        }

        unsafe fn realloc(&self, pointer: *mut u8, layout: Layout, size: usize) -> *mut u8 {
            observe();
            unsafe { System.realloc(pointer, layout, size) }
        }
    }

    pub fn set_thread_tracking(enabled: bool) {
        TRACK_THIS_THREAD.with(|tracking| tracking.set(enabled));
    }

    pub fn reset() {
        OBSERVATIONS.store(0, Ordering::Relaxed);
    }

    pub fn observations() -> u64 {
        OBSERVATIONS.load(Ordering::Relaxed)
    }
}

#[cfg(test)]
pub(crate) use allocation_probe::{observations, reset, set_thread_tracking};

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct CounterSnapshot {
    pub ffi_compute_entries: u64,
    pub input_copies: u64,
    pub output_copies: u64,
    pub workspace_growth_events: u64,
    pub designated_rust_allocations: u64,
}

#[derive(Debug, Default)]
pub struct RuntimeCounters {
    ffi_compute_entries: AtomicU64,
    input_copies: AtomicU64,
    output_copies: AtomicU64,
    workspace_growth_events: AtomicU64,
    designated_rust_allocations: AtomicU64,
}

impl RuntimeCounters {
    pub fn observe_compute_entry(&self) {
        self.ffi_compute_entries.fetch_add(1, Ordering::Relaxed);
    }

    pub fn observe_input_copy(&self) {
        self.input_copies.fetch_add(1, Ordering::Relaxed);
    }

    pub fn observe_output_copy(&self) {
        self.output_copies.fetch_add(1, Ordering::Relaxed);
    }

    pub fn observe_workspace_sizing(&self, allocations: u64) {
        if allocations == 0 {
            return;
        }
        self.workspace_growth_events.fetch_add(1, Ordering::Relaxed);
        self.designated_rust_allocations
            .fetch_add(allocations, Ordering::Relaxed);
    }

    pub fn snapshot(&self) -> CounterSnapshot {
        CounterSnapshot {
            ffi_compute_entries: self.ffi_compute_entries.load(Ordering::Relaxed),
            input_copies: self.input_copies.load(Ordering::Relaxed),
            output_copies: self.output_copies.load(Ordering::Relaxed),
            workspace_growth_events: self.workspace_growth_events.load(Ordering::Relaxed),
            designated_rust_allocations: self.designated_rust_allocations.load(Ordering::Relaxed),
        }
    }

    pub fn reset(&self) {
        self.ffi_compute_entries.store(0, Ordering::Relaxed);
        self.input_copies.store(0, Ordering::Relaxed);
        self.output_copies.store(0, Ordering::Relaxed);
        self.workspace_growth_events.store(0, Ordering::Relaxed);
        self.designated_rust_allocations.store(0, Ordering::Relaxed);
    }
}
