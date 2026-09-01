# ALG-01R2 dual audit

## PHYS–MATH

Conventions remain `(-,+,+,+)` and `epsilon_123=+1`. The exceptional
`VI_-1/9` object remains a dynamical sector of `VI_h`, not a twelfth
Bianchi algebra type.

The two new obligations are canonical-witness obligations:

```text
sigma13_carrier_present
sigma23_carrier_present
```

They prove that the state representation has not deleted either independent
carrier. They do not require either component to be nonzero on every physical
solution. Hence zero-shear and one-carrier physical submanifolds remain
admissible.

The exact group parameter is represented by

```json
{"denominator":9,"numerator":-1,"type":"rational"}
```

rather than a JSON number. This keeps the dimensionless identity `h=-1/9`
distinct from its binary64 approximation. No dimensional rate is substituted
for the canonical fingerprint.

Known limits retained:

- public algebra count remains eleven;
- the exceptional momentum and group constraints remain unchanged;
- proper/improper `O(3)` covariance is inherited unchanged from ALG-01R1;
- no connection, curvature or Einstein equation is promoted here.

## PHYS–MATH–CODE

Equation-to-code path:

```text
TypeSpec.wl + Witnesses.wl
  -> ALG01R2ExactIdentity.wl
  -> ALG01R2CanonicalComparison.wl
  -> ALG01 / ALG01R1 / ALG01R2 MUnit suites
```

TDD result:

```text
RED:   63 predecessor PASS + 7 expected failures
GREEN: 77 PASS / 0 FAIL / 0 NOT_EVALUATED
```

Adversarial coverage:

| case | pre-R2 gate | ALG-01R2 gate |
| --- | ---: | ---: |
| canonical witness | 1 | 1 |
| delete Sigma13 only | 1 | 0 |
| delete Sigma23 only | 1 | 0 |
| delete both | 0 | 0 |

All eight hostile mutations are detected. A machine-real `signed_h` is
rejected and hashes differently from the exact-AST specification.

## Ranked findings

- P0: none.
- P1: closed — individual carrier deletion; exact-rational identity collapse.
- P2: open outside this node — GEO-02 generic API still needs Jacobi admission.
- P2: open outside this node — W2 abstract formula-content and executable
  definition gates require repair and restacking.
- P3: GitHub Actions remains unobserved; the connected fresh-Wolfram and
  Dropbox-restored replay is the evidence used here.

## Plot/CRAG boundary

Python plot generation returned `ClientError`; Wolfram `CloudExport` also
returned `$Failed`. No plot artifact was fabricated. The exact four-row
adversarial table is retained as the primary diagnostic evidence.

CRAG verdict:

- Correctness: the new gate accepts only the intact canonical witness.
- Retrieval: it matches the SSOT statement that Sigma13 and Sigma23 remain
  independent in the exceptional sector.
- Augmented: individual and simultaneous deletion mutations are all covered.
- Generation: the next admissible question is input admission to the
  Levi-Civita connection, not curvature promotion.

Surviving claim:

```text
ALG_01R2_EXACT_IDENTITY_AND_TWO_CARRIER_WITNESS_VERIFIED
```

Forbidden claim:

```text
BACKGROUND_READY / CURVATURE_READY / ALL_FAMILY_SOLVER_READY / PASS_RF04
```
