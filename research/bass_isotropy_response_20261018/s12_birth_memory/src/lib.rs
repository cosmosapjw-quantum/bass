//! Isolated S12 full birth-memory tangent; original S9/S10 owners are unchanged.
pub mod birth;
pub mod core;

#[cfg(feature = "history")]
#[path = "../../s11_p246/rust/projector.rs"]
pub mod projector;

#[cfg(feature = "history")]
pub mod history;
