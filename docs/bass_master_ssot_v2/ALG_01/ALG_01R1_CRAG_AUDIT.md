# ALG-01R1 plot-driven CRAG audit

**Stage:** `ALG_01R1`  
**Diagnostic figure:** https://www.wolframcloud.com/obj/7c247cb5-8dc5-490a-af46-85d679051752  
**Figure role:** adversarial diagnostic only; not a publication or solver figure.

## 1. Plot data

### Exceptional shear-survival obligation

```text
canonical VI_-1/9 witness  1
shear-deleted witness       0
```

### Structure-constant covariance residual L1

```text
Type II, proper SO(3)                0
Type II, improper O(3)               0
VI_-1/9, proper SO(3)                0
VI_-1/9, improper O(3)               0
wrong improper transform without det(R)  4
```

## 2. Plot reading

The left panel shows the intended firewall: the physical branch remains
admissible on special zero-shear submanifolds, but the selected bounded
witness ceases to satisfy its representation-completeness obligation when the
exceptional shear carriers are deleted.

The right panel shows exact covariance for all four admitted frame cases. The
only nonzero bar is the hostile parity mutation that treats `n` as an ordinary
tensor under an improper transformation.

## 3. CRAG loop

### Correctness

PASS. The plotted values are direct exact-algebra outputs, not fit residuals or
floating-point tolerances. The four admitted covariance residuals are exactly
zero and the mutation residual is exactly `4`.

### Retrieval

PASS with scope. The result agrees with the project SSOT statements that
`VI_-1/9` is an exceptional sector, that off-diagonal shear survives the
admissible chart, and that `n` acquires a `det(R)` factor under improper frame
changes. External literature is used only as contextual support.

### Augmented checks

PASS for the bounded witnesses:

- Type II and exceptional VI_-1/9;
- proper and improper orthogonal transformations;
- canonical versus shear-deleted exceptional witness;
- non-orthogonal frame input rejected;
- missing-pseudotensor-sign mutation detected.

This is not a random or exhaustive O(3) sampling theorem. Exact tensor
intertwining for the selected generators is the scoped evidence.

### Generation

The evidence predicts that a later connection/curvature generator must use the
same transform firewall. It does **not** yet establish covariance of connection
coefficients, curvature, Einstein equations or kinetic multipoles.

## 4. Adversarial verdict

Surviving claims:

```text
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED
ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED
```

Rejected claim:

```text
THE_OLD_FIVE_MUTATION_SUITE_WAS_SUFFICIENT_FOR_ALG01_CLOSEOUT
```

Narrowed interpretation:

```text
The exceptional witness proves representation survival.
It does not impose nonzero off-diagonal shear on every physical solution.
```

## 5. Environment note

The project research executor requests Python-generated plots. Python and
container-backed plot creation returned an execution-environment `ClientError`
in this session. The exact diagnostic was therefore generated with Wolfram
Language from the same values. No Python plot gate is claimed as passed.
