# PHYS–MATH–CODE audit — SYNC-MAP-02C R3

## Disposition

`PASS_RELATION_AND_SOURCE_COVERAGE / PHYSICS_IMPLEMENTATION_UNCHANGED`

R3 repairs federation metadata and verification. It changes no REI, REC, HTT
or BASS physical source module.

## Equation-to-code map

| Contract | Actual source path | Current role |
|---|---|---|
| Doppler, aberration, solid angle, absolute-temperature pullback | `htt/obsstat/lorentz_sky_pullback.py` | HTT output-only local-observer implementation and BASS export consumer |
| Photon energy drift and direction flow | BASS photon SSOT; REC characteristic consumer; REI group-redshift dependency | BASS-owned formulas, not yet in the canonical EquationIR export |
| Exact BASS/REC pins | `src/rei_bianchi/bass_integration_substrate.py` | REI custody/reference interface, not numerical physics |
| FLRW control Hubble and grouped redshift flow | `src/rei_bianchi/b2b_physical_model.py` | REI control/discretization path, not generic Bianchi transport |
| H/He electron density and state simplex | `monolithic_model_b2a.py`, `primary_exact_zero_model.py` | REI-owned thermochemistry |
| Finite-tau transmission and species allocation | `multigroup_hhe_transmission.py` | REI-owned radiative-transfer closure |
| Source-bound four-site native operator | `source_bound_mprk_sdirk_operator.py` | Intentionally nonconstructible typed blocker |

The current HTT WU-011 head is eight commits beyond the head pinned by the
02D relation map, but `htt/obsstat/lorentz_sky_pullback.py` retains the exact
same Git blob `c518cdd0dcdd3ca628c71f6dd9e6a75e174ba805`. Thus no physical
Lorentz-pullback drift is observed. This does not remove the need for a pinned
consumer binding at 02F.

## TDD and executable verification

The closeout contract was added before R3 production data. Exact head
`00a31c5e363449bd4ebe4d78c48b21cb9aca14ce` produced the intended failed
workflow run `33604001631` because the R3 classification, complete matrix and
hardened verifier were not yet present.

After the minimal repair, workflow run `33604725967` showed:

- fail-closed R3 verifier: PASS;
- ten mutation-sensitive unit tests: PASS;
- Python compilation: PASS;
- JSON parse and 22-row CSV parse: PASS;
- repository hygiene: FAIL only because ordinary `git diff --check` treats
  Markdown's intentional two-space hard breaks in pre-existing R2 documents as
  trailing-whitespace errors.

The hygiene false positive is preserved rather than relabelled as a full pass.
The workflow is repaired separately to retain strict non-Markdown checking and
to allow exactly two terminal spaces in Markdown, rejecting one, three or more
spaces and tabs.

## Mutation coverage

The tests execute the production verifier over temporary mutated copies and
require stable rejection codes for:

- compound owner;
- stale four-formula union;
- missing source row;
- source blob mismatch;
- premature 02E gate bypass.

The canonical path also checks the exact 22 path/blob map, 12 relation records,
class counts, BASS14 no-rederivation result, six consumer mappings, frozen 02D
workflow identity and withheld claims.

## Code-path findings

1. The previous nine-file evidence gap is closed by an exact 22-row relation or
   exclusion matrix.
2. The compound BASS+REC pin record is replaced by two atomic upstream-owner
   records while retaining REI as adapter owner.
3. The four-formula next-stage scope is replaced by the six-record REC+HTT
   union.
4. 02E remains held in the classification record; no source or workflow can
   infer readiness from the REC map alone.
5. The exact photon SSOT remains formula authority, not solver implementation.
6. The source-bound Rust operator still fails typed rather than falling back to
   Python/JAX.

## Regression risks

- A future REI source-tree change invalidates the fixed 22-path matrix and must
  fail before promotion.
- A future HTT local-pullback blob change requires 02D drift reclassification.
- The shared EquationIR compiler must preserve the `n=-e` adapter rather than
  choosing one sign by name matching.
- Full-sky physical Jacobian and blackbody pullback must not absorb mask,
  interpolation or estimator response.
- Passing metadata tests must not be presented as numerical Bianchi or
  first-interval validation.

## Required before 02E implementation

- final exact-head workflow success after the Markdown-aware hygiene repair;
- frozen head/tree readback for 02C and 02D;
- connected Wolfram receipt recorded as stateless rather than native;
- PR body and federation control pointer updated to six formulas;
- append-only Dropbox and Atlassian publication receipts.

## Claim boundary

`RELATION_CLASSIFICATION_AND_GOVERNANCE_ONLY_NO_PROVIDER_NUMERICAL_PARITY_OR_SCIENCE_PROMOTION`.
