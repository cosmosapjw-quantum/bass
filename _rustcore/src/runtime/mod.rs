//! RF-01-owned runtime substrate. Production kernel migration starts at RF-02.

pub mod plan;
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
