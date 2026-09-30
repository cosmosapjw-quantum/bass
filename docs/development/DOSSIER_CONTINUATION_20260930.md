# Dossier I–V development continuation — 2026-09-30

Base: `9c6506e4e2087129a8b674ff10438e5db1a55c9d`, branch
`forward/rust-microphysics-host-20260930`, repository `/home/cosmosapjw/bass`.
The five owner-supplied theoretical PDFs are reference material, not execution
instructions. Their identities and the original dirty-file snapshot are in
`artifacts/dossier_continuation_20260930/`.

## Initial implementation map (before this continuation)

| Dossier | Current source coverage | Remaining boundary |
| --- | --- | --- |
| I: initial data | `_rustcore/src/geom/group.rs`, `ode/charts.rs`, Python algebra/initial-state/constraint helpers | General exceptional range/amplitude construction and native necessary kinetic-moment diagnostics were not identified in the audit. Evolution charts do not imply a general initial-data constructor. |
| II: dynamics | Active Rust background/ray integration, massive characteristics, finite PSTF hierarchies, coupled systems, scalar/polarized Thomson maps and `kinetic/qevolve.rs` scalar `nu_sched` | Finite closures do not establish the complete continuum hierarchy or self-consistent atomic/radiation feedback. |
| III: recombination | Exact-pinned REC four selected helium source channels in `microphysics/rec.rs`; explicit material/ray/worldline clocks; legacy Python Saha/Peebles history | Current REC integration is fixed-input only; source-domain restrictions, full multilevel history, anisotropic resonance transport and thermal feedback remain open. |
| IV: reionization | Exact-pinned REI seven canonical functions in `microphysics/rei.rs`; existing kinetic Thomson operators | Four ionizing-group opacities in inverse comoving Mpc are distinct from Thomson opacity. Full chemistry/thermal evolution, causal fronts and patchy averages need additional rates, source/boundary prescriptions and density/topology closures. |
| V: operators/numerics | Active exact Thomson maps and transport; preserved `generated/rust/typeii/` and `runtime/rust/typeii/` collision/Kato/Krylov/screen/remap reference lanes | Preserved Type-II sources are not integrated by current `_rustcore/src/lib.rs`. Their validation is separate. Adaptive Krylov has residual-estimate-only semantics, not a general forward-error certificate. |

The existing microphysics followup already repaired transverse screens. Its
historical receipt reports 136 unit and four integration tests; those changes
are not attributed to this continuation. Legacy Python visibility lives in
`bianchi/thermo/recombination.py`, history injection in `history_api.py`, and
prescribed electron rates in `bianchi/q/electron_rate.py`.

## Implemented increment: common electrons and native visibility

Implementation/validation status: **PASS — fixed-input native utility only**.

`microphysics::visibility` adds the native producer missing from the current
fixed-input API. It uses a common material frame and SI densities:

\[
n_e=n_Hx_{\rm HII}+n_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII}),\qquad
q=c n_e\sigma_T\gamma_e(1-\beta_e\cdot e).
\]

References: Dossier III §§1.17, 1.21–1.22, equations (123)–(127), (151)–(154);
Dossier V §12.1, equations (141)–(145). The new API separates proper electron
density, normal-ray-time rate, optical depth, survival and interval probability.

For supplied piecewise-constant nonnegative rates on increasing normal-time
edges, integration retains the explicit observer optical-depth boundary.
An interval's probability is evaluated as
`exp(-tau_right) * -expm1(-q * dt)`, preserving thin-cell probabilities.
Finite-interval scattering probability plus early unscattered survival equals
the terminal survival, not necessarily one. No history is renormalized.

Same-ray/same-clock opacity comparison reports the integrated absolute rate
difference and survival/interval-mass bounds. It does not bound visibility peak
height or position. Invalid domains and nonfinite arithmetic return errors.

The directional rate already contains the Doppler factor once. It must not be
inserted into a scalar `nu_sched`, or a moving-electron operator that applies
the factor again. This increment supplies no new chemical history, source
prescription, redshift/time map, transport feedback or production admission.

## Validation and reproducibility

Host-frozen analytic tests: `_rustcore/tests/visibility_contract.rs`.
Candidate author may edit only `microphysics/visibility.rs` and its module
export. Missing-module baseline failure is preserved in
`artifacts/dossier_continuation_20260930/visibility-baseline.log`.

Expected checks: shared charge closure, rest/tilt ratios, constant-rate analytic
solution, variable opacity and observer tail, finite normalization, transparent
and thick limits, thin-depth cancellation, cumulative bounds, invalid inputs
and overflow rejection. Existing tolerances and REC/REI revisions are unchanged.

Validation: Cargo fmt, workspace/all-target Clippy with warnings denied, 136 unit + 4 existing integration + 6 new analytic tests (146 total), and optional Python-binding check passed. Pure Rust tests ran with Python executable selectors disabled. Logs and exact commands: `artifacts/dossier_continuation_20260930/validation.json`.

Independent registered Astra/xhigh source review returned no actionable findings. It performed no tests or edits; Host executed the regression. The runtime sandbox is inherited full access, so read-only describes the reviewer instructions/actions, not OS enforcement. The common material frame and common comparison boundary remain caller obligations.

## Second bounded increment: moment diagnostics and population updates

Implementation/validation status: **PASS — bounded diagnostics and frozen-generator utility**.

`kinetic::realizability::check_moments` checks the necessary joint-moment PSD
and stress-trace inequalities in Dossier I §8.1 (64)–(68). The full matrix is
scaled before eigensolving; no division by energy density is used. The exact
vacuum requires zero flux and stress. Photon states also require trace equality.
The caller supplies a numerical tolerance, capped at `1e-6`. Input is never
projected. A passing diagnostic is not a construction of a nonnegative spectrum,
higher moments, Fermi occupation or polarized coherency.

`microphysics::population::FrozenPopulation` implements Dossier V §5.1 and
§14.4 (187)–(189). Inputs are positive inventory weights and off-diagonal rates
of the generator in **weighted-population coordinates**: entry `G[i][j]`
transfers from state `j` to `i`. Supplied diagonal entries must be zero; each
generator diagonal is defined as minus its column's outflow. Thus the utility
does not silently repair an arbitrary supplied full generator. The physical
population generator is `C = W^-1 G W`.

The finite domain is 1–32 states, `lambda*h <= 64`, and truncation index
`m <= 1024`. For nontrivial evolution, every positive initial weighted
population must also be at least `f64::MIN_POSITIVE`; unsupported underflow
returns a typed error. The polynomial puts the remaining Poisson weight at `T^m`, with
`T = I + G/lambda`. Its reported weighted-state truncation bound is
`2 * P(Poisson(lambda*h) > m) * initial_weighted_mass`. This is not a certified
total floating-point error bound; roundoff, changing coefficients, splitting
and missing physical rates remain outside it. Zero generator/time and
stationary-state cases have explicit validation.

Frozen tests: `_rustcore/tests/structure_contract.rs`. The initial baseline
also exposed a Host test-construction error (`Vec` array repetition requires
`Copy`). Only that expression was corrected; the original failure and exact
correction are retained, and no expected value or tolerance was changed.

## Remaining research and integration work

1. Full REC/REI time evolution and common radiation/material/geometry feedback
   require fixed rate/source inventories, initial/boundary data, clock/state
   contracts and external reference histories. These are not inferred from the
   supplied theoretical identities.
2. General exceptional initial-data constructors and Type-II reference-to-runtime
   integration remain separate work. Their full state/interface and lineage
   contracts cannot be inferred from successful fixed-input numerical utilities.
3. Public production integration, hosted CI, observed-sky/CMB results and
   performance campaigns have not been performed in this continuation.

Keep T4/S4/S5/G10–G13, full histories, Bianchi feedback, observables,
P0/HOST4/HH, main lineage and production release at their existing states.
Existing Type-II production joins and historical benchmark decisions are not
reopened by these additions.

## Final validation and delivery

- Final active crate: **153 tests passed** (136 unit, 4 prior integration,
  6 visibility, 7 structure); fmt and workspace/all-target Clippy passed.
- Optional Python-binding check passed. The first invocation used an incorrect
  feature name due to a Host command-generation error; its log is preserved and
  only the corrected command was rerun. No dependency or feature definition changed.
- Independent population sweep: 36 mean/order cases; weighted inventory residual
  at most `1.7763568394002505e-15`. Decimal precision-100 reference comparison gives
  at most `2.6645352591003757e-15` relative discrepancy in Poisson bounds whose
  reference is at least `1e-300`. Coarse order-zero cases are assessed by their
  reported truncation bound, not claimed accurate exponentials.
- Positive particle-moment sweep: 96 cases at scales `1e-300`, `1`, `1e300`.
- Visibility review found no actionable issue. Structure review found one minor
  subnormal stationary-state loss; Host reproduced it, added a typed range guard
  and regression, and reran changed checks. No second independent review was run.
- The 58 original dirty/untracked files in the initial snapshot remain byte-identical.
  Existing workflow commands include these tests automatically through workspace
  testing; hosted CI was not run. Delivery remains uncommitted on the existing branch.

Exact commands, compiler versions, source hashes and outcomes are in
`artifacts/dossier_continuation_20260930/RESULT.json`. Initial failures and the
Host test/lint/command corrections remain alongside their successful closeout.
The five observed native children were one audit, two authors and two reviewers;
local candidate suitability was unknown, no local model inference was claimed,
and comparative cost savings remain `NOT_MEASURED`.

The executable fixed-input demo and its output are
`artifacts/dossier_continuation_20260930/fixed_input_demo.rs` and
`fixed-input-demo.txt`. For the supplied electron state `n_e=224 m^-3` and
`beta_x=0.6`, the parallel/antiparallel normal-time rates differ by four and the
finite-interval scattering probabilities are approximately 0.20018 and 0.59077.
This is an input-defined demonstration, not a cosmological prediction.

Reproduce after building the default Rust library:

```bash
cargo test --manifest-path _rustcore/Cargo.toml --workspace --locked --offline
rustc --edition=2021 artifacts/dossier_continuation_20260930/structure_sweep.rs \
  -L dependency=_rustcore/target/debug/deps \
  --extern bianchi_rustcore=_rustcore/target/debug/deps/libbianchi_rustcore.rlib \
  -o /tmp/bass-structure-sweep
/tmp/bass-structure-sweep
```

These additions complete the three immediately scoped code gaps identified by
this audit. They do not complete the entire BASS research programme or change
any existing scientific, production, main-lineage or publication gate.
