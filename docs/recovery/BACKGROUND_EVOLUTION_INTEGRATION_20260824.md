# Background Evolution Integration Receipt — 2026-08-24

## Purpose

This receipt records a preservation-oriented integration of the recovered
`bianchireview87` background-evolution source with the current bounded DAG,
polarization, and electron-authority material. It is a backup and review
checkpoint. It does not promote any scientific authority row or enable a
production collision path.

The integration target is the new child branch
`agent/recovery/background-evolution-v87-integrated-20260824`; the immutable
recovery branch is not moved.

## Git inputs

| Role | Ref | Commit | Treatment |
| --- | --- | --- | --- |
| immutable recovery base | `agent/recovery/background-evolution-v87-source-20260824` | `dc546a07c5d05cd68b6d43c9ca4c41a57d8d5c81` | parent of a new child integration branch |
| Type-II aggregate and DAG realignment | `agent/bass-dag-realignment-20260821` | `af467a974cfd9bd8ccd59870e5a03c8099f23db1` | merge into the child branch |
| corrected bounded B1/polarization aggregate | `agent/b1-authority-reconciliation-20260821` | `38fd8b08b81d9969f81fb6299b23cc0673380a4c` | merge into the child branch as frozen R&D material |
| electron E1–E4 preservation source | `agent/backup/bass-8b1e1-e4-plus-applicability-20260823` | `e4c9308af11e3234a344aeab487188a5550b1a3c` | audited blob transplant only; not merged as ancestry |

The recovery base was created from the external snapshot whose SHA-256 is
`6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84`.
The supplied archive contains no Git metadata, so it is an identified external
snapshot rather than proof of earlier repository ancestry.

The final child-branch commit and tree identifiers are intentionally recorded
outside this file in GitHub and the Atlassian control-plane receipt, avoiding a
self-referential commit digest.

The recursive recovery tree contains 421 blobs. Of these, 408 source-tree
paths match the isolated archive extraction by Git blob ID and mode, with zero
mismatches; the remaining 13 are recovery metadata/provenance files. The DAG
six-path delta, B1 75-path delta, 421-path recovery tree, and 21-path E1–E4
transplant have pairwise-zero overlap at their integration seams. GitHub
read-back remains the authority for the actual merge results.

## Selected integration surface

The recovery branch already contains the allowlisted v87 background source.
This integration preserves the active-tree E1–E4 electron checkpoint modules,
focused tests, independent audit programs, machine-readable contracts, and the
CODATA-2022 constants required by those modules. Exact file digests are in
`provenance/integration/PRESERVED_ELECTRON_CHECKPOINT.sha256`. Independent
review found an accepted-domain near-null numerical failure, so these modules
are a frozen, unpromoted checkpoint rather than trusted active authority.

The E1–E4 material remains bounded as follows:

- E1: independent electron test-field and frame adapter.
- E2: proper-density collision-rate and schedule authority.
- E3: cold-Thomson validity and explicit consumer contract.
- E4: trajectory-aligned support and integration-orientation authority.
- Scalar Q collision generation remains `SCALAR_Q_KERNEL_UNRESOLVED`.
- Solver, JAX, Rust, and production collision-loop wiring are not enabled.
- No authority-row promotion is made by this integration.

## Explicit exclusions

The following branches or materials are not merged:

- `agent/g-pol-liouville-ii-b2b-upload` and all staging/quarantine tips,
  including the closed-unmerged PR #12 staging head.
- `agent/recovery/runtime-interruption-20260811-inventory`, which is a
  superseded quarantine inventory.
- `agent/route-a-a0`, `agent/route-a-a0-v2`, and old harness/automation bundles.
- The E4 backup branch as a whole; its own contract marks it preservation-only.
- Legacy scalar-Q and moving-collision ownership in `bianchi/q/rate.py`,
  `bianchi/thermo/history_api.py`, `bianchi/matter/collision_moving.py`, and
  `_rustcore/src/kinetic/qevolve.rs` as an authority replacement.
- Rust 1.94.1 distributions, xAct, original archives, generated reports,
  third-party papers, caches, and other vendor payloads.

The existing v87 runtime files are preserved for recovery provenance, but this
receipt does not claim that their legacy collision semantics are compatible
with or wired to E1–E4.

## Verification evidence

Fresh focused execution in the restored v87 source tree produced:

| Gate | Result |
| --- | --- |
| E1 electron state/frame tests | `13/13 PASS` |
| E2 collision-rate tests | `13/13 PASS` |
| E3 cold-Thomson validity tests | `20/20 PASS` |
| E4 trajectory authority tests | `28/28 PASS` |
| E2 independent rate audit | `2000 cases PASS`; worst Lorentz-scalar residual `8.49594e-15` |
| E3 hostile audit | `1201` Klein–Nishina and `1200` boost cases `PASS` |
| E4 hostile audit | all orientation/domain lanes `PASS`; max integral relative error `1.02656e-15` |
| P9 screen audit | `PASS`; worst leak `1.657e-15` |
| E1–E4 JSON contracts | parse/shape validation `PASS` |
| Python byte compilation | restored source, tests, and audits `PASS` |

The historical full-suite claims (`1682` Python tests and `122` Rust tests)
were not rerun on this host because the complete JAX/diffrax/maturin/Cargo
dependency stack is unavailable. That gap is `UNVERIFIED`, not a pass.

## Independent review findings retained as stop boundaries

- The E1 binary64 frame composition is not stable over its full declared
  `|beta| < 1` input domain. For the reproduced near-null pair
  `(-0.40499928034712473, 0.19483031443833956, -0.89331782221904)` and
  `(-0.40499928034731597, 0.19483031443830184, -0.8933178222189615)`, E1
  returns relative gamma `0.9999999999999998` while an 80-digit evaluation
  gives `1.0006827776097833`; the composed matrix has maximum Lorentz residual
  `0.7964699272409437`. E2 consumes this transform, so E1/E2 are
  `UNVERIFIED_NUMERIC_DOMAIN` for ultrarelativistic/nearly-comoving inputs.
  No certificate or collision rate from that domain may be promoted or wired
  until the adapter is made cancellation-stable or explicitly fails closed
  and the hostile vector is a regression test.
- `ColdThomsonCertificate` in the preserved E3 source is publicly
  constructible and does not independently recompute its invariants. A caller
  can therefore manufacture a value whose metadata says
  `CERTIFIED_COLD_DELTA`. This does not affect E4's separately factory-locked
  trajectory certificate, and no runtime consumer is wired here, but the E3
  certificate must be treated as `KNOWN_UNSAFE_TO_PROMOTE` until its
  constructor is sealed and adversarial regression tests pass.
- The preserved E4 machine contract names
  `BASS-8B.1E.5_direction_dependent_Q_collision_generator_authority` as its
  then-current next node. The later canonical Jira control-plane decision
  supersedes that historical pointer with
  `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING`. The original E4 contract byte is
  retained for provenance; it is not the current routing authority.

## Next controlled node

The next node remains `BASS-8B.2A_TYPED_ELECTRON_STATE_BINDING`. Its first
preconditions are to make E1/E2's near-null transform cancellation-stable or
fail-closed and to seal/adversarially test the E3 certificate constructor. It
must then bind the E1–E4 state and consumer contracts without silently enabling
the unresolved scalar-Q generator or legacy Rust collision ABI. `BASS-3`
remains blocked by `BASS-8` until the relevant join gates are explicitly
satisfied.
