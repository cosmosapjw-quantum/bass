# GEO-02 PHYS–MATH–CODE audit

## Verdict

`PASS_NO_P0_P1_IN_SCOPED_GEO_02_SOURCE`

The source is admissible for the stated connection-only scope. This is not a
curvature, background or runtime promotion.

## Changed executable paths

```text
wolfram/BASS/Kernel/Geometry/LeviCivitaConnection.wl
wolfram/BASS/Kernel/init.wl
wolfram/BASS/Tests/GEO02CartanConnection.wlt
wolfram/scripts/run_stage.wls
```

No Rust, Python production, REC, REI or `htt_base` path is changed.

## TDD history

The exact ALG-01R1 restored source was loaded before implementation. Five
required GEO-02 public APIs were absent:

```text
BASS`Geometry`LeviCivitaConnection
BASS`Geometry`ConnectionTorsionResidual
BASS`Geometry`ConnectionMetricCompatibilityResidual
BASS`Geometry`ConnectionOneFormTerms
BASS`Geometry`ConnectionCovarianceQ
```

Observed RED:

```text
0 PASS / 5 FAIL / 0 NOT_EVALUATED
parent source loaded: true
```

The first GREEN attempt did not pass:

```text
6 PASS / 9 FAIL / 0 NOT_EVALUATED
```

The cause was a line-leading `&&` in the symmetric-input predicate, rejected by
the Wolfram parser. The repair replaced it by `And[...]`; no formula,
coefficient, state, tolerance or expected result changed.

Post-repair focused replay:

```text
15 PASS / 0 FAIL / 0 NOT_EVALUATED
```

Fresh full-stack restored replay:

```text
W0/W1 + ALG-01R1 + GEO-02
78 PASS / 0 FAIL / 0 NOT_EVALUATED
Wolfram 15.0.1 Linux-x86-64
xAct/xTensor 1.3.0
manifold/CovD/Riemann registration PASS
```

## Positive tests

- API and fail-closed input contract;
- torsion-free connection on all five witnesses;
- metric compatibility on all five witnesses;
- exact Type II component table;
- exact Type V component table;
- Type IX `Gamma=C/2` identity;
- connection and one-form component counts;
- proper and improper `O(3)` covariance.

## Adversarial tests

- missing-`det(R)` transformation of `n` under an improper frame change is
  detected through a nonzero connection residual;
- nonsymmetric or wrongly shaped algebra input is rejected;
- the earlier parser-invalid source is preserved in the Dropbox initial
  overlay while the corrected source is stored in `fix1/`.

## Independent symbolic checks

A separate evaluator, not the production test helper, reconstructed the Koszul
formula for general symbolic `a` and symmetric `n`. It obtained exact zero for
all torsion and metric-compatibility components. A separate linear solve found
one solution to the homogeneous 54-equation/27-unknown uniqueness system:
all connection differences vanish.

## Remaining nonblocking risks

### P2 — constant-frame scope

`ConnectionCovarianceQ` covers constant spatial `O(3)` frame changes. A
spatially dependent frame would require derivative terms, and the full
four-dimensional time connection of a time-dependent triad includes the
triad-rotation rate. Those terms belong to later tetrad/background stages.

### P2 — curvature not yet generated

The existence of a correct connection does not validate the curvature formula,
Ricci contractions or Einstein constraints. GEO-03 must add independent
Cartan-second-equation and commutator-based curvature oracles before promotion.

### P3 — sparse representation

`ConnectionOneFormTerms` uses exact `PossibleZeroQ` pruning. The public source
contains no floating threshold, but later symbolic conditional domains must
remain fail-closed rather than assuming undecidable terms vanish.

### P3 — connected evaluator persistence

The Wolfram evaluator is stateless. Every authoritative replay must continue to
activate the exact-pinned xAct archive and reconstruct the committed source.

## Claim firewall

```text
AUTHORIZED:
  GEO_02_LEVI_CIVITA_CONNECTION_WITNESSES_VERIFIED
  GEO_02_TORSION_METRIC_AND_O3_COVARIANCE_VERIFIED

WITHHELD:
  SPATIAL_CURVATURE_OR_RICCI_DERIVATION
  BACKGROUND_EINSTEIN_MATTER_EQUATIONS
  CONSTRAINT_PROPAGATION
  ALL_FAMILY_SOLVER_SUPPORT
  NUMERICAL_PARITY
  CROSS_REPOSITORY_COMPATIBILITY
  SCIENCE_VALIDITY
  BASS_RF04_PROMOTION
```
