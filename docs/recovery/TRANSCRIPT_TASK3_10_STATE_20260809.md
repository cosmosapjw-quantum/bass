# Transcript-only Task 3–10 implementation state

## Evidence boundary

This document preserves the most specific implementation and validation claims still
available from the interrupted long-running conversation. It is a reconstruction index,
not a source tree, Git object, test log, review attestation, or scientific PASS receipt.
Every row remains `TRANSCRIPT_ONLY` until its behavior is recreated under observed RED,
fresh GREEN, cumulative regression, and independent review.

The current GitHub repository and every visible local Git object store fail to resolve the
short commit identifiers below. The original workspace-root `.git` path is masked by an
empty read-only tmpfs in this runtime, so absence behind that mount cannot be proved.

## Stage ledger

| Task | Transcript locator | Last reported behavior and validation | Recovery status |
|---|---|---|---|
| 3 | unknown | Later cumulative selectors refer to Tasks 3–6 and Tasks 3–10, but no Task 3 commit, tree, file list, or standalone output survives here. | `TRANSCRIPT_ONLY`; source/Git object `MISSING_OR_MASKED` |
| 4 | unknown | Later history/state regressions refer to a v1 history API and inherited state boundaries, but no Task 4 commit or exact implementation survives here. | `TRANSCRIPT_ONLY`; source/Git object `MISSING_OR_MASKED` |
| 5 | `3347547` review head | Task 6 began from an independently reviewed Task 5 baseline. No tree or review file is present. | `TRANSCRIPT_ONLY`; locator unresolved locally and remotely |
| 6 | `eaf13af`, fix `4e1a3b6` | Geometry/curvature completion added an absolute curvature residual budget, rejected nonfinite curvature, and made returned arrays strongly bytes-backed and immutable. A paired fixture reportedly rejected residual `1.46e-11` and accepted the `/3` scale residual `9.09e-13`. Final reported gates: focused 37, Fermi selector 3, Tasks 3–6 regression 208; independent review `Approved`. | `TRANSCRIPT_ONLY`; both locators unresolved |
| 7 | `54fb3bf`; later fix SHAs not retained | `bianchi.full.fluids` reportedly built literal four-dimensional connection contractions and conservative `E,Q_i` evolution from `nabla_mu T^{mu nu}=0`, with primitive/EMT/CPL paths, FLRW `Omega'=-3 h Omega`, class-A/B affine checks, `h=0`, causal inverse, and mass-shell evolution. A spatial lower-index swap separated curvature storage order from the final derivative slot. Review fixes aligned exact `|v|<1`, normalized extreme finite failures, and made one-ULP multi-component speed decisions deterministic. Final reported gates: focused 51, cumulative 259, inherited audit 2; no P0/P1/P2 after re-review. | `TRANSCRIPT_ONLY`; initial locator unresolved and later fix commits unknown |
| 8 | `29327f9`, fix `e993691` | `bianchi.full.history.HistoryV2` reportedly provided canonical field hashing, one-time provider sampling, grid/coverage validation including holes, log-coordinate interpolation, a v1-only adapter, and non-monotonic redshift revisits. Review fixes rejected hostile `str`/digest subclasses, raw/subclass provenance objects, bool/string/complex coercions, conversion-exception leakage, and revalidated exact nominal objects at the state boundary. Final reported gates: focused 64 with warnings promoted, legacy 5, cumulative 323; 10,000 scalar/vector byte-parity probes. | `TRANSCRIPT_ONLY`; both locators unresolved |
| 9 | `6d786e1`, fix `c3d45f3` | `baryon_opacity`, `directional_opacity`, and `optical_depth_visibility` reportedly enforced evolved-baryon ownership, SI/cgs conversion, one Doppler factor, and visibility sign. Fixes used `frexp`/`ldexp` scale arithmetic to distinguish physical zero identities from representational underflow, guarded extreme positive trapezoids, normalized hostile conversions, and added a nonzero class-B evolution proof. Final reported gates: focused 77, expanded cumulative 427; 20,000 product/ratio probes at at most 3 ULP and 20,000 trapezoid probes at at most 1 ULP. | `TRANSCRIPT_ONLY`; both locators unresolved |
| 10 | no final commit | `bianchi.full.sources.EMTSource` reportedly reached frozen/readonly value semantics; Mode A identity and asymmetric-frame photon/FD moments; Mode B `q^4 dlnq det(M)` measure; exact Mode-A/B discrete overlap; and deterministic adjacent-pair reduction with zero, duplicate, cancellation, and overflow cases. The last report said 65 focused tests were GREEN after normalizing finite-cell-sum overflow. Full cumulative regression, commit, and independent review were not reported. | `TRANSCRIPT_ONLY_IN_PROGRESS`; source and commit `MISSING_OR_MASKED` |

## Reconstructable interfaces and invariants

The transcript supports the following future RED tests but not an implementation claim:

1. Geometry must fail closed on absolute, not scale-relative, curvature budget violations;
   nonfinite results must never pass through NaN comparisons; public arrays must be deeply
   immutable, not merely `writeable=False` views.
2. Fluid conservation must use an independently assembled four-dimensional affine
   connection, preserve the recorded lower-index convention, reproduce the FLRW fixed
   limit, and evolve the mass-shell constraint consistently.
3. `HistoryV2` must validate all fields before hashing, sample a provider exactly once,
   separate coverage holes from endpoint coverage, preserve canonical scalar/vector bytes,
   and distrust hostile subclasses or nominal objects received across provenance boundaries.
4. Opacity must derive electron density from the evolved baryon state, apply exactly one
   directional Doppler factor, preserve every representable positive result without
   intermediate underflow, and give the documented optical-depth/visibility sign.
5. Kinetic EMT moments must distinguish Mode A carrier normalization from Mode B phase
   measure, preserve frame orientation, use deterministic reduction, and fail closed on
   invalid grids, species, carriers, frames, and nonfinite/overflowing cells.

## Missing information that must not be invented

- The approved Task 1–10 plan and the exact Task 3–5 APIs/file lists.
- Full SHA-1 identifiers and commit trees for every short locator.
- Task 7 fix-round commit identifiers.
- Task 10's final cumulative test result, commit, and independent review.
- The exact source/test bodies for `bianchi/full` and their dependency baseline.
