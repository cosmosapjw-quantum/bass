# ALG-01 Plot-Driven CRAG Adversarial Audit

**Plot role:** contract-admission diagnostic; not a physical observable.  
**Wolfram-rendered view:** https://www.wolframcloud.com/obj/93d5e966-90f9-44ff-86d9-4280b293e596  
**Machine data:** `CRAG_PLOT_DATA.csv`  
**Regenerator:** `wolfram/scripts/plot_alg01_crag.wls`

## Plot reading

The five canonical witnesses occupy the exact zero-failure baseline. Every
hostile mutation produces at least one failed contract:

| Mutation | Failed contracts | Additional exact signal |
| --- | ---: | --- |
| Jacobi break | 3 | six nonzero full-Jacobi components |
| IX inertia flip | 1 | Jacobi still zero; branch identity fails |
| V nonzero `n` | 3 | zero-`n`, rank and inertia fail |
| exceptional `h` drift | 2 | group residual `5`, momentum residual `-2` |
| exceptional momentum drift | 1 | group residual `0`, momentum residual `-12` |

The figure deliberately separates canonical witnesses from hostile mutations.
The bar height counts failed ALG-01 contracts and has no invariant physical
norm interpretation.

## C — Correctness

- Canonical witnesses have zero failed contracts.
- All five adversarial mutations are detected.
- A Jacobi-preserving IX inertia mutation still fails branch admission, showing
  that branch identity is not reduced to the Jacobi condition.
- Exceptional group and momentum mutations are separately visible.

**Result:** PASS.

## R — Retrieval

The expected zero and nonzero patterns agree with the project SSOT structure
decomposition, the eleven-branch atlas predicates and the exceptional
VI_-1/9 constraint surface. External SciSpace references are used only for
methodology and exceptional-sector context; they do not override project
signs or normalization.

**Result:** PASS within project conventions.

## A — Augmentation

The probe spans:

- zero-structure Class A (I);
- rank-one Class A (II);
- pure-vector Class B (V);
- full-rank same-sign Class A (IX);
- exceptional Class B (VI_-1/9);
- Jacobi, inertia, rank, signed-`h`, group and momentum mutations.

It does not span all eleven public labels, arbitrary frames or dimensional
physical data.

**Result:** PASS with bounded coverage.

## G — Generation

The surviving prediction for the next node is narrow:

> A Cartan connection/curvature generator may consume only an admitted
> `BianchiTypeSpec` plus physical dimensional `a,n` data and must reproduce
> these five coframe witnesses before any family-wide or background claim.

No prediction is made for Einstein dynamics, arbitrary-ell transport,
observables or statistics.

## Mutation verdicts

- sign/rank mutation claim: surviving;
- exceptional constraint admission: surviving;
- five-witness algebra generator: surviving;
- eleven-family geometry generator: not yet tested;
- background-ready claim: rejected at this stage.

## Final CRAG classification

```text
SURVIVING CLAIM:
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED

NARROWED TO:
exact algebra input, branch predicates, Jacobi and coframe witnesses

REJECTED/DEFERRED:
connection, curvature, Einstein background, all-family solver,
transport, observables and statistics
```
