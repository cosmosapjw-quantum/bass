# SYNC-MAP-02D PHYS–MATH–CODE Audit

## Current verdict

```text
SOURCE_RELATIONS_DURABLE
WOLFRAM_EXACT_ALGEBRA_PASS
EXACT_HEAD_STDLIB_WORKFLOW_PENDING
NO_SHARED_EXPORT_OR_SCIENCE_PROMOTION
```

This audit asks whether the mathematical relation classes correspond to the
actual HTT code paths rather than to documentation names alone.

## Equation-to-code map

| Mathematical or processing object | Exact HTT source | Code role | Relation class |
|---|---|---|---|
| `D=gamma(1+beta.n)` and boosted-chart inverse | `htt/obsstat/lorentz_sky_pullback.py` | production output-side implementation | pending BASS import / consumer implementation |
| exact aberration and deaberration | `htt/obsstat/lorentz_sky_pullback.py` | production output-side implementation | pending BASS import / consumer implementation |
| `dOmega_tilde/dOmega=D^-2` | `htt/obsstat/lorentz_sky_pullback.py` | exact regression surface | pending BASS import / independent oracle role |
| positive `d=1` temperature pullback | `htt/obsstat/lorentz_sky_pullback.py` | production output adapter | pending BASS import plus HTT adapter |
| quadrupole `l=1,l=3` response | `htt/obsstat/boost_response.py` | independent STF/harmonic oracle | independent oracle, authority effect NONE |
| boost-before-source-transfer ordering | `htt/obsstat/processed_boost_response.py` | production synthetic source-map path | HTT-owned processed extension |
| processed linear generator | `htt/obsstat/processed_boost_linearization.py` | differentiated processed path | HTT-owned processed extension |
| joint `l=0..5` solve and retained `l=2..5` carrier | `htt/obsstat/processed_boost_operator.py` | production synthetic processed path | HTT-owned processed extension |
| `(3,32,49)` coefficient Jacobian | `htt/obsstat/processed_boost_jacobian.py` | response/diagnostic object | HTT-owned processed extension |
| fixed-axis and FWL parity | `htt/obsstat/processed_boost_parity.py` | audit-only alternate route | independent oracle, authority effect NONE |
| mask/source-tail identifiability atlas | `htt/obsstat/processed_boost_identifiability.py` | Task-7B analysis path | HTT-owned processed extension |

## Source identity and lineage

The classification exact-pins eight Git blobs from two immutable reviewed
heads:

```text
WU-010 PR #442  29427a1f7f2c5d46e43ffe03053c4ac13e969228
WU-011 PR #444  978fbe612a570b9973b17c51237965f16b630fc4
```

The WU-010 source explicitly states that the implementation is an output-side
local boost and not global matter tilt, a foreground model, or a Bianchi
classifier. The WU-011 sources preserve the same boundary and add only
synthetic mask/beam/pixel/HEALPix/joint-fit response machinery.

## Production, adapter, and oracle separation

- `lorentz_sky_pullback.py`: production HTT local-observer consumer
  implementation of common frame formulas.
- `boost_response.py`: coefficient-level independent oracle; it is not a
  cosmological forward solver.
- `processed_boost_response.py`, `processed_boost_linearization.py`,
  `processed_boost_operator.py`, `processed_boost_jacobian.py`, and
  `processed_boost_identifiability.py`: HTT-owned processed extensions.
- `processed_boost_parity.py`: audit-only parity route, explicitly not an
  alternative production estimator.

This separation prevents a shared full-sky formula from acquiring ownership
of mask-specific estimator semantics, and prevents an HTT implementation from
becoming a second BASS common-formula authority.

## Contract verifier

`scripts/verify_sync_map02d_htt_relations.py` enforces:

1. exact BASS parent and HTT heads;
2. eight unique 40-hex Git blob pins;
3. twelve unique relation and formula IDs;
4. exact class-count and shared-gap sets;
5. no duplicate or unresolved authority;
6. local/global/electron-tilt/data-fit firewalls;
7. zero Wolfram residuals and detected hostile mutations;
8. DAG closure, acyclicity, required 02C/02D prerequisites, and 02E→02F
   ordering;
9. equality of the JSON and CSV relation projections;
10. preservation of all load-bearing withheld claims.

The stdlib test file includes negative tests for a missing HTT prerequisite,
global-tilt reclassification, duplicate formula ownership, and silent
empirical-beta promotion.

## Strongest failure modes

### P0 — semantic owner inversion

Failure: classify the HTT exact local boost as a new common authority or as
BASS global tilt.

Guard: every shared relation names `bass` as owner; the firewall requires
`NO_ACTIVE_HTT_IMPLEMENTATION` for global tilt and finite-electron-tilt
collision.

Current status: guarded in committed data and verifier.

### P1 — processed/full-sky conflation

Failure: treat a mask/beam/weighted-fit response as the exact Lorentz theorem.

Guard: processed objects use `HTT_OWNED_PROCESSED_EXTENSION`; the full-sky
Doppler/aberration objects use pending BASS import classes.

Current status: guarded in committed data, source-role table, and literature
lock.

### P1 — premature shared export

Failure: let 02E start after REI mapping alone or after HTT mapping alone.

Guard: both `02C_REI -> 02E_SHARED_EXPORT` and
`02D_HTT -> 02E_SHARED_EXPORT` are mandatory. A mutation removing the HTT
edge remains acyclic but is still rejected.

Current status: guarded in Wolfram and Python contracts.

### P1 — unexecuted exact-head software checks

Failure: infer Python GREEN merely from committed source or unrelated
workflows.

Guard: dedicated `sync-map02d-htt-relations` workflow runs the stdlib verifier,
mutation tests, compilation, JSON/CSV parsing, and text hygiene.

Current status: pending at this audit revision. No automated exact-head PASS is
claimed here.

## Numerical and scientific non-claims

This relation node does not execute HEALPix maps, estimate an observable,
compare data, fit beta, validate Task-7C, integrate Bianchi backgrounds, or
run REC/REI providers. It therefore has no numerical-performance or science
claim. The HTT Task-7B quantitative results are source context, not evidence
that the four-repository federation is ready.

## Ranked findings

```text
P0  none open in the committed bounded classification
P1  exact-head dedicated software workflow not yet read back at this revision
P2  no native repository-file Wolfram replay; plugin algebra is exact but
    separately scoped
P2  source-blobs are exact-pinned but cross-repository import hashes cannot be
    issued until BASS 02E records exist
P3  visual SVG hostile print audit is a documentation-quality gate only
```

## Completion criterion

The bounded 02D node may be called `PASS` only after:

```text
dedicated exact-head workflow = SUCCESS
PR head/tree and all new blobs = read back
Wolfram exact receipt = preserved
PHYS-MATH and PHYS-MATH-CODE boundaries = preserved
02E remains blocked by incomplete 02C
```
