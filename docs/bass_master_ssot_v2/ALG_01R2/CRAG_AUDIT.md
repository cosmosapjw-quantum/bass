# ALG-01R2 plot-based CRAG adversarial audit

**Plot:** https://www.wolframcloud.com/obj/a33bb7a3-b9b9-4274-9e78-e1da550b333c  
**Data:** `CRAG_PLOT_DATA.csv`

## Plot reading

The canonical exceptional witness preserves both independent off-diagonal shear carriers. Deleting either `Sigma13` or `Sigma23` reduces the represented carrier dimension from two to one, and deleting both reduces it to zero. Every mutation is rejected by the repaired witness-obligation gate.

## C — Correctness

The plot matches the executable carrier report:

```text
canonical          {Sigma13, Sigma23} -> PASS
Sigma13 deletion   {Sigma23}          -> REJECT
Sigma23 deletion   {Sigma13}          -> REJECT
both deleted       {}                 -> REJECT
```

The gate is deliberately a canonical-witness representation test. It is not a physical assertion that every solution must have both amplitudes nonzero.

## R — Retrieval

The result agrees with the formula SSOT and literal atlas: the exceptional `VI_-1/9` sector is not a twelfth algebra type and its authority chart preserves independent `Sigma13` and `Sigma23` directions where permitted by the exceptional momentum constraint.

## A — Augmented checks

- exact `h=-1/9` semantic projection contains no machine-real value;
- a machine-real mutation is rejected;
- proper and improper frame covariance regressions remain green;
- all previous rank, inertia, Jacobi, group and momentum hostile mutations remain detected.

## G — Generation

The repaired gate predicts that a future connection/background state layout which omits either exceptional carrier must fail before equation generation. It does not predict connection or curvature coefficients.

## Claim classification

**Surviving claim**

```text
ALG_01_EXACT_SEMANTIC_IDENTITY_VERIFIED
ALG_01_INDEPENDENT_EXCEPTIONAL_CARRIERS_VERIFIED
```

**Rejected claim**

```text
ALG_01R2 proves connection, curvature, Einstein background or all-family solver readiness
```
