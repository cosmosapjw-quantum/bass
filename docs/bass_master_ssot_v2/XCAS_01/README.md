# XCAS-01 — external formula-verification package lane

```text
authority_effect: NONE
```

This Draft stage attempts downloadable computer-algebra and tensor-calculus
packages against bounded BASS witnesses.  A package agreement is independent
evidence only.  It never selects a BASS convention, repairs an EquationIR,
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
```

Package-level independence and algebra-engine independence are not conflated.
Two different packages using SymPy count as two package implementations but
only one underlying algebra engine.

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
DEFERRED_RESOURCE_HEAVY
```

A blocked package remains blocked.  The aggregator never relabels a missing
binary, incompatible Python version, unsupported ABI, or package runtime error
as a successful formula check.

## Existing independent package result

`BowenPing/STensor` 1.0.1 was downloaded through `PacletSymbol` in a fresh
Wolfram 15.0.1 evaluator.  It independently reproduced an exact zero
Minkowski Einstein tensor and the diagonal Bianchi-I identity

```text
G_00 = (a'/a)(b'/b) + (a'/a)(c'/c) + (b'/b)(c'/c).
```

This is an independent tensor-package implementation but not an independent
CAS engine because it shares the Wolfram Language kernel.

## Hard claim firewall

```text
NO_02E_SEMANTIC_PROMOTION
NO_02F_SEMANTIC_CLOSEOUT
NO_CONSUMER_PARITY_PROMOTION
NO_PROVIDER_ADMISSION
NO_SCIENCE_PROMOTION
```

In particular, external agreement cannot waive these already accepted defects:

- the pre-hardening PR #99 weighted-blackbody pullback dependency graph;
- zero-boost executable regularization;
- the geodesic-normal specialization;
- ray-parameter naming and unit adapters;
- PR #101's weakened REI residual receipt;
- the distinction between the HTT full-field pullback and the pre-pulled-value
  Doppler primitive.

## Deferred package

SageMath/SageManifolds is a strong independent geometry axis, but a full Sage
image is too large for this bounded CI stage.  It is explicitly deferred to
`XCAS-02`, not silently counted as attempted or passed.
