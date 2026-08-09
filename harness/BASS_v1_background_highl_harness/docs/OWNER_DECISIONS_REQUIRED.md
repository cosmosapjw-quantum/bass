# Owner decisions required before code intake

## OD001 — High-ell completion criterion

Choose adaptive finite `ell_max` with a declared integer production floor `L_prod >= 2`.
Supply canonical decimal-string `atol`/positive `rtol` pairs for low-ell observables and
exactly the high-ell channel rows enabled by OD002. Every enabled species/spin row must
pass separately for the retained bulk and closure guard at at least three allocations.

## OD002 — Release-blocking physics sectors

Resolve the exact boolean map for global tilt; photon I/E/B/V; exactly massless,
collisionless neutrinos;
exact electron-frame Thomson scattering; recombination; and reionization. The recommended
starting profile enables global tilt, I/E/B, and neutrinos; keeps V and collision/history
optional; and requires I=true and E/B together.

## OD003 — `bianchi_phase_r` authority

Confirm the pinned repository as a read-only symbolic/numerical oracle at
`539fcd6acc81dfd19d05951c2c5cbc3602eda077`. Production-upstream authority is not a valid
OD003 branch because it conflicts with the installed oracle firewall. Execution and every
remote write remain locked behind later, separate authorization.

## OD004 — Rust and supplied partial Rust-core role

State whether a Rust backend and PyO3 surface are release-blocking, whether Rust 1.94.1 is
a strict historical pin/minimum/not required, and whether the supplied partial archive is
excluded, read-only reference (recommended), or only a quarantined production candidate.
Resolution alone never authorizes installation, import, overlay, build, execution, or write.

All resolved values require a hash-bound explicit owner-decision receipt. That receipt
confirms OD001–OD004 only and grants no read, write, build, execution, or installation
authority. After it is recorded, issue `G-OD0` separately for read-only canonical
code intake using an exact `bass.code_read_authorization/v1` record bound to the owner
receipt. `IA0` remains a separate later decision for code write, build, execution, and
dependency installation.
