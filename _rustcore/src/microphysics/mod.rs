//! Exact-revision, pure Rust REC and REI host boundary.
//! These fixed-input dispatches do not establish a full thermochemical history.
pub mod frame;
pub mod rec;
pub mod rei;

#[cfg(test)]
mod tests;
