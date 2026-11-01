//! RF-01-owned runtime substrate. Production kernel migration starts at RF-02.

pub mod plan;
/// Opt-in original Type-II background callback. No RF-01 dispatch substitution.
pub mod typeii_host;
/// Source-linked Type-II Liouville and proper-electron opacity, not production dispatch.
pub mod typeii_photon_host;
pub mod workspace;

use std::fmt;

#[derive(Debug)]
pub enum RuntimeError {
    InvalidConfig(String),
    InvalidBuffer(String),
    PlanMismatch(String),
    WorkspaceBusy(String),
    WorkspaceState(String),
    UnsupportedCapability(String),
    PoolConstruction(String),
    ContainedPanic(String),
}

impl fmt::Display for RuntimeError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidConfig(message)
            | Self::InvalidBuffer(message)
            | Self::PlanMismatch(message)
            | Self::WorkspaceBusy(message)
            | Self::WorkspaceState(message)
            | Self::UnsupportedCapability(message)
            | Self::PoolConstruction(message)
            | Self::ContainedPanic(message) => formatter.write_str(message),
        }
    }
}
