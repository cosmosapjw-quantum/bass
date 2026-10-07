//! Exact-revision, pure Rust REC and REI host boundary.
//! These fixed-input dispatches do not establish a full thermochemical history.
pub mod frame;
pub mod population;
pub mod rec;
pub mod rei;
pub mod rei_visibility;
pub mod visibility;
pub mod visibility_clock;

#[cfg(test)]
mod tests;
