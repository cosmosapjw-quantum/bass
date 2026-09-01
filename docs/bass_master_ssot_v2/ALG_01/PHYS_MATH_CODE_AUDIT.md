# ALG-01 PHYS–MATH–CODE AUDIT

**Verdict:** `PASS_EXACT_WITNESS_PATH / NO_BACKGROUND_PROMOTION`  
**Implementation commit/tree:** `be30f27acbe9c8be66aaa1e0831ab6f7cb158294` / `fe389bce6ddbaaabc957651a014b4f319d998ebe`

## 1. Equation-to-code map

| Formula or contract | Code owner | Evidence |
| --- | --- | --- |
| `C^gamma_{alpha beta}` | `Geometry/StructureConstants.wl::BianchiStructureConstants` | exact canonical and hostile witnesses |
| `n^{ab}a_b` | `JacobiVectorResidual` | all canonical zero; hostile nonzero |
| full Lie Jacobi tensor | `JacobiTensorResidual` | all canonical zero; hostile six-component failure |
| Cartan coframe terms | `CartanCoframeTerms` | exact literal terms for II, V, IX, VI_-1/9 |
| reconstruction | `CartanReconstructionQ` | exact equality for all five witnesses |
| branch schema | `Bianchi/TypeSpec.wl` | fail-closed registry validation |
| exceptional constraints | `Witnesses.wl::ExceptionalVIminusOneNinthResiduals` | zero canonical; two independent mutations |
| stage admission | `ValidateCanonicalWitness`, `ValidateHostileWitnesses` | `.wlt` regression |

## 2. Code-path reality

The actual execution path is

```text
exact a,n,shear witness
 -> BianchiTypeSpec predicate contract
 -> structure constants
 -> vector Jacobi + full tensor Jacobi
 -> antisymmetry + Cartan rendering/reconstruction
 -> rank/inertia/Class-B/exceptional predicates
 -> fail-closed witness report
```

There is no call into background Einstein equations, matter evolution,
photon hierarchies, Rust production code, REC/REI providers or `htt_base`.
The empty/future module names do not count as implementations.

## 3. TDD and exact replay

TDD RED was observed before implementation for

```text
BASS`Bianchi`MakeBianchiTypeSpec
BASS`Geometry`BianchiStructureConstants
BASS`Bianchi`ValidateCanonicalWitness
```

Fresh verification used new stateless Wolfram kernels and exact Dropbox text
mirrors of the GitHub blobs.

| Suite | Result |
| --- | ---: |
| W0 exact xAct environment regression | 6 succeeded / 0 failed |
| W1 convention, dimension and semantic-IR regression | 13 / 0 |
| ALG-01 exact committed `.wlt` replay | 33 / 0 |
| independent focused witness probe | 25 / 0 |
| total canonical stage tests | 52 / 0 |
| runner/Paclet/init static parse | 3 / 3 PASS |

Runtime identity:

```text
Wolfram 15.0.1 for Linux x86 (64-bit)
xAct/xTensor 1.3.0
xPerm 1.2.4
xAct archive SHA-256
7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
```

The first exact `.wlt` replay passed 33/33, but the surrounding summary code
attempted an invalid `TestID` extraction and emitted `Part::pspec1`. A second
fresh replay removed that non-test diagnostic and again passed 33/33 with no
extra message. Only the clean replay is admitted to the stage receipt.

## 4. Hostile mutation coverage

| Mutation | Required detection |
| --- | --- |
| Class-A Jacobi break | `a_zero`, vector Jacobi and full tensor Jacobi |
| IX inertia flip | branch inertia despite Jacobi remaining valid |
| Type-V nonzero `n` | zero-`n`, rank and inertia predicates |
| exceptional `h` drift | signed `h` and group constraint |
| exceptional momentum drift | exceptional momentum constraint |

All five are detected. This prevents a generic Lie algebra satisfying Jacobi
from being mislabelled as a requested Bianchi branch.

## 5. Serialization and schema boundary

The type specification and witness report have public JSON schemas. Exact
rational values are kept in Wolfram authority; a downstream JSON renderer must
preserve rational semantics rather than silently convert authoritative values
to binary64. The W1 exact-scalar IR remains the canonical route for formula
coefficients.

## 6. Numerical and performance scope

No floating-point numerical integration, tolerance, cutoff, sparse backend,
JIT, benchmark or observable is involved. Consequently:

- numerical maturity: not applicable at ALG-01;
- performance claim: forbidden;
- plot: adversarial contract diagnostic only;
- no production code path was changed.

## 7. Ranked findings

### P0

None within the tested witness path.

### P1

- No connection/curvature/background equation is implemented; downstream
  geometry work must not infer it from the presence of Cartan terms.

### P2

- The connected environment did not execute `run_stage.wls` from a complete
  repository checkout. Instead, exact `.wl/.wlt` blobs were restored and run,
  while the runner, Paclet and init files were parsed separately. This is
  sufficient for the scoped module claim, but not a native repository-runner
  or CI claim.
- The JSON schemas are interface contracts; schema presence is not an
  independent tensor oracle.

### P3

- Git commits are unsigned.
- GitHub Actions status must be read separately; no CI result is inferred from
  the connected Wolfram replay.

## 8. Genuinely fixed

- common Bianchi structure input is executable and exact;
- canonical fingerprints are firewalled from physical magnitudes;
- Jacobi is checked in two representations;
- branch identity is checked independently of Jacobi validity;
- the exceptional VI_-1/9 group and momentum constraints are independently
  exercised;
- future stages have a stable machine-readable admission report.

## 9. Still uncertain or deferred

- connection signs after lowering to an explicit tetrad/xCoba basis;
- spatial Ricci tensor and scalar;
- Einstein constraint propagation;
- all eleven public labels;
- physical chart transitions and Type-IX recollapse;
- arbitrary-ell kinetic code generation.
