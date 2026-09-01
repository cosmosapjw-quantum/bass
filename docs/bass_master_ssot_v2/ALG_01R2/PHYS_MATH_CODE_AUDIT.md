# ALG-01R2 PHYS–MATH–CODE audit

**Stage:** `ALG_01R2`  
**Verdict:** `PASS_EXACT_SOURCE_REPLAY_WITH_NO_DOWNSTREAM_PROMOTION`

## 1. Equation-to-code map

| Contract | Production symbolic path | Test path |
| --- | --- | --- |
| exact structure constants and Jacobi | `wolfram/BASS/Kernel/Geometry/StructureConstants.wl` | `ALG01BianchiAlgebra.wlt` |
| proper/improper frame covariance | `wolfram/BASS/Kernel/Geometry/FrameCovariance.wl` | `ALG01R1ExceptionalAndCovariance.wlt` |
| branch predicates and exact `h` identity | `wolfram/BASS/Kernel/Bianchi/TypeSpec.wl` | `ALG01R2ExactIdentityAndCarriers.wlt` |
| canonical and hostile witnesses | `wolfram/BASS/Kernel/Bianchi/Witnesses.wl` | all three ALG test files |
| public JSON contracts | `wolfram/schemas/bianchi-*.schema.json` | static schema parse gate |
| stage orchestration | `wolfram/scripts/run_stage.wls --stage ALG_01R2` | fresh source replay |

## 2. TDD evidence

Before implementation, six expected failures were reproduced and recorded:

- semantic type-spec projection API absent;
- semantic type-spec hash API absent;
- independent carrier-report API absent;
- deleting only `Sigma13` was accepted;
- deleting only `Sigma23` was accepted;
- exact rational and machine-real values collided in generic RawJSON.

The production code was then changed minimally to satisfy these gates.

## 3. Fresh replay result

The exact W0/W1, ALG-01R1 and ALG-01R2 text sources were restored from Dropbox into a fresh stateless Wolfram kernel. xAct/xTensor `1.3.0` and xPerm `1.2.4` loaded successfully.

```text
81 succeeded
0 failed
0 not evaluated
```

Additional readback:

```text
all five type specs valid                         PASS
semantic registry SHA-256 length                 64
semantic projection contains no machine Real    PASS
machine-real signed_h mutation rejected          PASS
canonical Sigma13 carrier present                PASS
canonical Sigma23 carrier present                PASS
all eight hostile mutations detected             PASS
```

Semantic registry SHA-256:

```text
e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762
```

## 4. Code-path reality

The carrier checks are computed from the supplied witness shear matrix. They are not fixed receipt constants and are not inferred from a document label.

`BranchPredicateReport` combines:

- rank and inertia computed from `n`;
- signed `h` computed from `a` and the transverse determinant;
- Jacobi vector and full tensor residuals;
- structure antisymmetry and Cartan coframe reconstruction;
- exceptional group/momentum residuals;
- witness-only carrier obligations.

The physical branch predicate list remains separate from witness obligations.

## 5. Regression and failure containment

- Existing W0/W1 convention and IR tests remain green.
- Existing five canonical ALG witnesses remain green.
- Existing proper/improper `O(3)` covariance tests remain green.
- The new exact AST path rejects `_Real` instead of silently rounding it.
- The repair does not modify Rust/Python production numerics, photon equations, REC/REI providers or `htt_base` outputs.

## 6. Remaining code risks

- **P2:** current `GEO-02` is a separate descendant experiment and is not yet rebased on this exact-identity repair.
- **P2:** connection code must publish an explicit index-order adapter to the legacy Python Einstein-frame convention.
- **P2:** curvature and background equations are not part of this receipt.
- **P3:** GitHub Actions may not select this Wolfram-only path; connected fresh replay is the current execution evidence.
- **P3:** Dropbox text mirrors are reconstruction-grade UTF-8 backups, not byte-preserving binary archives.

## 7. Required next gate

Before curvature or Einstein background work, create a composed geometry branch from this tested source and require:

```text
torsion residual = 0
metric-compatibility residual = 0
legacy index-order adapter residual = 0
I/II/V/IX/VI_-1/9 witness connection checks
proper/improper frame covariance
no curvature promotion from connection-only evidence
```

## 8. Claim boundary

```text
ALG_01R2_EXACT_IDENTITY_AND_CARRIER_REPAIR_ONLY
NO_CONNECTION_CURVATURE_BACKGROUND_NUMERICAL_OR_SCIENCE_PROMOTION
```
