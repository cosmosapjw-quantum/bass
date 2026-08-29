# RF-04 external-review reconciliation

## Decision

Resume from `d43e4e9039f8cd9303340ed216e76a650138adef`, tree
`27f37630c42c5c39e705a84202d687363260d908`, not from the older RED-only
commit. The external-review fixes are a direct child of
`4508cb3af776d2a058d71bbe8b95f9bfe62b35ed` and change 15 paths.
They are retained, not replayed or replaced.

The previous A2 execution instruction is withdrawn. This is a semantic
correction, not a checksum workaround. Preserve the original ZIP and PR #53.
A2 selected legacy `bianchi/q/polstate.py`: GL-product Lagrange remapping,
explicit RK2/RK4, and no separate Kato stage. That is not the current audited
Type-II donor:

* `runtime/rust/typeii/typeii_polarized_remap.rs` implements common-screen
  **convex** remapping and rejects negative weights. A generic 6x6 Lagrange
  stencil is not an interchangeable implementation.
* `typeii_polarized_runtime.rs` has an actual `frozen_kato_step`, and
  `typeii_polarized_runtime_physical.rs` has a checked adaptive counterpart.
  Equilibrium-projector Kato transport is not the same operator as geometric
  screen parallel transport.
* `typeii_polarized_liouville.rs` explicitly stops before angular remapping,
  collision composition and observables. Its repaired bounded midpoint
  integrator is not the legacy RK4 instruction.

Source blobs and exact revisions are in `CONTRACT.json`. The source locations
can be read as `https://github.com/cosmosapjw-quantum/bass/blob/` followed by
that commit and the listed path. No formula authority is inferred from a
branch name, a ZIP name, or a self-reported residual.

## What the submitted fixes support

The attached independent review is the basis for this disposition. Its SHA-256
is `5d91a9eae593a8f96be090a67ddfe773dcf60a55054fdd249764ba481690079d`.
The review was static with separate numerical probes; it did not execute the
submitted repository. Its old truncated-A2 finding applies to the artifact
it inspected, not automatically to every later copy of that ZIP.

| Review item | Evidence at d43e4e9 | Remaining claim boundary |
|---|---|---|
| C1 | Nonzero, stage-varying Type-II fixtures and Lebedev-26/full l=2 rank/fourth moments are present. | Fixture adequacy is not a native trajectory proof. |
| C2 | Tautological rate-dual/projector/nonnormal claims were removed. | Compiled native mutants must still fail a state-array differential test. |
| C3 | Old missing-module/import RED remains genuine boundary absence evidence. | It never demonstrated physics detection power. Do not replay it for credit. |
| C4 | New independent dense oracle and public-boundary differential tests are provided here. | Native differential tests have not passed in this environment. |
| M1 | Off-equilibrium raw/AP refinement was added. | Three decreasing errors do not establish equal asymptotic order, all boosts or native AP consistency. |
| M2 | Donor guards use trace-normalized checks. | Some full public tests still use absolute metrics; new reference metrics test intensity scales 1e-120 to 1e120. |
| M3 | Remap/Liouville realizability gates were strengthened. | State PSD gates must also surround future public collision composition; Krylov basis vectors must NOT be treated as PSD radiation states. |
| M4-M5 | External-background refinement and bounded midpoint bisection are in the fix. | The reported Rust runs were not repeated here; substeps alone do not remove background reconstruction error. |
| M6 | A transport-support option and typed rejection exist. | The default remains the old antipodal margin. A real stencil builder must supply and consume its meaningful support bound. |
| M7 | Typed arithmetic, support and realizability errors were added. | Verify propagation through the native exception/member boundary. |
| M8 | Coordinate-golden regeneration and live-constant/comment-decoy checks were added. | A golden-parser test is not a public trajectory oracle. |
| M9 | Original full tests still hardcode historical authority constants. | New profile identity is fixture-loaded; immutable pins are distinct from mutable branch tips. |
| M10 | Boost propagation-direction and oriented-screen tests were added. | No E/B/TB/EB observable claim is established. |

The user's 39 Python / 85 minimal-crate Rust passes are recorded as
USER_REPORTED, not rerun or independently certified here. Source inspection
supports the existence of the changes, not every reported numerical outcome.

## Concrete progress in this change

`bianchi/kinetic/__init__.py` now provides thin dispatch to the three frozen
native symbols. It contains no numerical loop and never imports an oracle.
Its software tests use an explicit fake boundary, so they prove dispatch,
argument identity and fail-closed behavior, not native physics.

`tests/rf04/rf04_dense_oracle.py` independently assembles the scalar Thomson
matrix, rate-dual projector and complex-step Kato derivative, then uses dense
SciPy exponentials and block-phi1 actions. It reproduces the existing
`typeii_runtime::kato_aem2_step` composition and checks its small-step limit.
The adaptive counterpart already exists in `typeii_krylov_adapt.rs` with the
same ordering and a real residual-statistics ledger.

The scalar donor's A is **diagonal bolometric transport at fixed directions**.
It does not contain full angular advection. This slice must not be described
as a completed Bianchi polarized Einstein-Boltzmann trajectory. In particular,
Kato is subtracted from the middle Aeff; adding it as an extra physical source
changes the limiting generator.

The rest-frame polarized reference is a direct common-screen Thomson action
and an independent complex-Hermitian screen eigensolver. It is not a polarized
trajectory solver. Three disposable Python-oracle source mutants are killed
by numerical assertions; that does not close the compiled-native mutation gate.

## Next deliverable and unchanged final goal

The next bounded deliverable is a native, independently checked
`scalar_intensity_v1` + `fixed_grid_raw_v1` slice. It may advertise only that
combination. The full RF-04 tests remain intact and will still reject an
incomplete capability inventory. The terminal ceiling is
`PASS_RF04_SCALAR_RAW_SLICE_PROOF` together with `NO_PASS_RF04`.

The full polarized route still needs the five explicit contract decisions in
`CONTRACT.json`. Do not copy the withdrawn A2 answers into those gaps. Work on
the known scalar path is not blocked by those gaps or by old ZIP custody.
