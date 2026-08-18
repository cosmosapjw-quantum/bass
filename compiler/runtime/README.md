# G-RUNTIME-KATO-II

This layer consumes the generated Type-II physics kernels from PR #5 and adds
reference-level numerical time integration machinery.

Accepted runtime path:
- full-dimensional Arnoldi action for `exp(hA)y`;
- Pade13 scaling/squaring on the projected small matrix;
- augmented-exponential `phi1` action;
- Kato co-moving AEM2 composition;
- source-derived Type-II/RateSchedule regression on Lebedev-26.

## Fail-closed boundary

A truncated Krylov basis (`m_max < state dimension`) is deliberately rejected.
An experimental ad-hoc time-splitting/restart controller underestimated the
actual error. Adaptive/restarted exponential/phi actions require a dedicated
`phipm`/KIOPS-class implementation and verification gate.

This runtime is therefore a **reference backend**, not yet the scalable
production backend.

## RustCore integration map

Public BASS path:
`runtime/rust/typeii/typeii_runtime.rs`

RustCore integration fixture path used in verification:
`_rustcore/src/generated/typeii_runtime.rs`

Offline Cargo verification must be invoked from the `_rustcore` crate root so
that its `.cargo/config.toml` vendored-source replacement is discovered.

The public repo does not vendor the Rust toolchain or Cargo registry sources.
