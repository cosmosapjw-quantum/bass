# Runtime failure ledger

## R1 — cold Cargo invocation outside crate root

**Observed:** `cargo --locked --offline` failed to find vendored dependencies.

**Cause:** `.cargo/config.toml` source replacement is rooted in the uploaded
`_rustcore` crate tree; the verification command was initially invoked from a
different working directory/PATH context.

**Repair:** execute offline Cargo verification from the crate root with the
pinned Rust 1.94.1 toolchain on PATH.

**Classification:** operational verifier error, not physics/runtime failure.

## R2 — ad-hoc restarted Krylov acceptance is unreliable

**Observed:** for a deliberately small Arnoldi basis, residual-estimate and
step-doubling variants accepted results whose true error exceeded the requested
tolerance.

**Decision:** do not tune the heuristic. `m_max < n` now returns
`SubspaceTooSmall` and is tested as fail-closed.

**Follow-up:** implement a literature-grade adaptive `phi` action algorithm
(e.g. Niesen–Wright `phipm` or KIOPS-style adaptive Krylov) as a separate gate.
