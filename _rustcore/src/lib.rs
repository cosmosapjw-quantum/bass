//! BASS native Rust compute core. Python bindings are an optional feature.
pub mod core;
pub mod geom;
pub mod kinetic;
pub mod microphysics;
pub mod ode;
#[cfg(feature = "python-binding")]
mod python;
pub mod rays;
pub mod runtime;
pub mod thermo;

#[cfg(feature = "python-binding")]
mod bindings;
