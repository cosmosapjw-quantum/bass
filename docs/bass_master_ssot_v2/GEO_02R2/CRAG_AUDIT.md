# GEO-02R2 plot-driven CRAG audit

**Executable data:** `CRAG_PLOT_DATA.csv`  
**User-visible exports:**

```text
geo02r2_connection_sparsity.png
geo02r2_parity_mutation.png
geo02r2_index_permutation_repair.png
```

The Wolfram evaluator generated and read the same three data panels. Public
Cloud publication was unavailable in that evaluator, so the PNG exports are
presentation artifacts; the committed CSV and Wolfram test receipts remain the
machine-readable evidence.

## Plot reading

### Connection sparsity

```text
I          0
II         6
V          4
IX         6
VI_-1/9   10
```

The Type-I zero sentinel is exact. The exceptional witness is the densest of
the five sentinels, but this count is a canonical witness property rather than
a measure of physical complexity or a claim about all solutions.

### Improper-frame parity mutation

```text
correct O(3) transform   residual detection = 0
missing det(R) mutation  residual detection = 1
```

The visual separation agrees with the executable hostile test: treating the
Bianchi structure pseudotensor as an ordinary tensor under an improper frame
change breaks covariance and is detected.

### Gamma index permutation

```text
original direct permutation   failed componentwise contracts = 1
corrected permutation          failed componentwise contracts = 0
```

The plot makes the main stage repair visible. A round-trip-only test would not
have exposed mutually reversed adapters; the direct componentwise definition
did.

## C — Correctness

The plotted counts reproduce exact Wolfram results and the corrected
`18/18`, dual `33/33` and full `114/114` test runs. No floating-point
threshold enters the plotted quantities.

## R — Retrieval

The result is compatible with the admitted orthonormal-frame and
Levi-Civita-equivariance literature. Literature does not determine the
project’s index order or pseudotensor adapter; those remain executable
project-owned contracts.

## A — Augmented checks

The plotted claims survive:

- five branch sentinels rather than one;
- both proper and improper frame changes;
- the missing-`det(R)` mutation;
- exact parent semantic identity;
- preservation of both exceptional shear carriers;
- inherited W0/W1 and ALG-01/R1/R2 regression.

They have not been augmented to spatial curvature, time-dependent frame
rotation, matter or numerical integration.

## G — Generation

The surviving connection layer predicts that `GEO-03` must preserve:

1. the same generated and locked index orders;
2. ordinary tensor covariance of the connection-generated curvature;
3. pseudotensor parity only at the algebra-data boundary;
4. Type-I zero curvature;
5. independent exceptional shear carriers in later state layouts.

## Adversarial claim classification

### Surviving

```text
GEO_02R2_LEVI_CIVITA_CONNECTION_COMPOSED_ON_ALG01R2
GEO_02R2_TORSION_METRIC_O3_INDEX_ORDER_VERIFIED
GEO_02R2_PARENT_IDENTITY_AND_EXCEPTIONAL_CARRIERS_PRESERVED
```

### Narrowed

```text
GEO-02R2 verifies five canonical spatial-connection sentinels;
it does not establish all-eleven-family background readiness.
```

### Rejected

```text
connection verification implies spatial curvature correctness
connection verification implies Einstein background equations
connection verification implies numerical or scientific readiness
```
