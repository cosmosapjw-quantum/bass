//! RF-02C callback-free background event and trajectory substrate.

pub(crate) mod carrier;
pub(crate) mod events;
pub(crate) mod exact;
pub(crate) mod history;
pub(crate) mod trajectory;
pub(crate) mod type_ix_dae;

#[cfg(test)]
mod tests;
