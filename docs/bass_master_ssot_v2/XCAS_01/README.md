# XCAS-01 — external formula-verification package lane

```text
authority_effect: NONE
```

This Draft stage attempts downloadable computer-algebra and tensor-calculus
packages against bounded BASS witnesses. A package agreement is independent
evidence only. It never selects a BASS convention, repairs an EquationIR,
changes a semantic hash, or promotes a consumer implementation.

## Exact parent

```text
BASS PR #101
commit 32b8a89abbeaad5503cf0dfc59cfa5633a53ec3b
```

The first branch head is a genuine RED absence witness: the contract test
failed because the package probes and receipts were not present.

## Independence classes

```text
INDEPENDENT_TENSOR_CAS
  Cadabra2

INDEPENDENT_SCALAR_CAS
  Maxima
  REDUCE, when the Ubuntu package is available

INDEPENDENT_GR_PACKAGE_SHARED_SYMPY_ENGINE
  EinsteinPy
  OGRePy
  Pytearcat when core_calc=sp

INDEPENDENT_GR_PACKAGE_GIAC_ENGINE
  Pytearcat only when core_calc=gp is actually observed

INDEPENDENT_TENSOR_PACKAGE_SHARED_WOLFRAM_KERNEL
  BowenPing/STensor
  OGRe
  BlackHolePerturbationToolkit/GeneralRelativityTensors
```

Package-level independence and algebra-engine independence are not conflated.
Different packages using SymPy count as different package implementations but
only one underlying algebra engine. Likewise, STensor, OGRe and
GeneralRelativityTensors are independently implemented packages but share the
Wolfram Language kernel.

## Bounded probes

- Minkowski and diagonal Bianchi-I Einstein-tensor witnesses;
- exact aberration inverse and solid-angle Jacobian;
- the regular zero-boost coefficient;
- the weight-one blackbody pullback generator and its aberration-advection
  term;
- tensor antisymmetry, pair exchange and first Bianchi identities.

## Receipt statuses

```text
PASS
FAIL_FORMULA
BLOCKED_INSTALL
BLOCKED_RUNTIME
BLOCKED_HOSTED_RUNNER_INFRASTRUCTURE
DEFERRED_RESOURCE_HEAVY
```

A blocked package remains blocked. The aggregator never relabels a missing
binary, incompatible Python version, unsupported ABI, package runtime error, or
job that never obtained a runner as a successful formula check.

## Executed package results

Three independently implemented Wolfram tensor packages have actually run.

### BowenPing/STensor 1.0.1

Downloaded through `PacletSymbol` in a fresh Wolfram 15.0.1 evaluator. It
reproduced an exact zero Minkowski Einstein tensor and

```text
G_00 = (a'/a)(b'/b) + (a'/a)(c'/c) + (b'/b)(c'/c)
```

for diagonal Bianchi I.

### OGRe 2.0.0

Downloaded from the exact version tag as a 191955-byte source file with
SHA-256

```text
e745de7820861b942103e5614e518bcc5748155f81edb69ca42c28b70b87b66a
```

For

```text
g_mn = diag(-1,t^2,t^4,t^6)
```

it reconstructed

```text
G_mn = diag(11/t^2,-14,-9 t^2,-4 t^4)
```

with four exact-zero diagonal residuals and twelve exact-zero off-diagonal
residuals.

### GeneralRelativityTensors

Downloaded from exact source commit
`6e5a0b1e8af94c5368334b9e3ac5e9d83b92928d`. The archive was 223044 bytes
with SHA-256

```text
b4143ccae4e47021a03fea15b4f4835d9099c234fca1f2a9b37c9ed2be9f5d65
```

It independently reproduced the same complete Bianchi-I Einstein tensor with
all sixteen component residuals exact zero.

These are three independent package implementations but **not** three
independent CAS engines.

## Hosted-runner block

The Python, Cadabra2, Maxima and REDUCE jobs have not executed. Repeated
GitHub Actions runs produced seven failed job records with no allocated runner,
no steps and no logs. This is classified as

```text
BLOCKED_HOSTED_RUNNER_INFRASTRUCTURE
```

rather than package installation, runtime, or formula failure. The GitHub API
did not expose the underlying allocation or entitlement cause.

## Hard claim firewall

```text
NO_02E_SEMANTIC_PROMOTION
NO_02F_SEMANTIC_CLOSEOUT
NO_CONSUMER_PARITY_PROMOTION
NO_PROVIDER_ADMISSION
NO_SCIENCE_PROMOTION
```

In particular, external agreement cannot waive these accepted defects:

- the pre-hardening PR #99 weighted-blackbody pullback dependency graph;
- zero-boost executable regularization;
- the geodesic-normal specialization;
- ray-parameter naming and unit adapters;
- PR #101's weakened REI residual receipt;
- the distinction between the HTT full-field pullback and the pre-pulled-value
  Doppler primitive.

## Deferred package

SageMath/SageManifolds is a strong independent geometry axis, but a full Sage
image is too large for this bounded CI stage. It is explicitly deferred to
`XCAS-02`, not silently counted as attempted or passed.
