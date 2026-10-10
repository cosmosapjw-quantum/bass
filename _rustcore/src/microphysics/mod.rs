//! Exact-revision, pure Rust REC and REI host boundary.
//! These fixed-input dispatches do not establish a full thermochemical history.
pub mod axisym_observables;
pub mod frame;
pub mod population;
pub mod rec;
pub mod rei;
pub mod visibility;

#[cfg(test)]
mod tests;
