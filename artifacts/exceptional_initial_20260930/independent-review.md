- **P2 — Normalization can erase geometry and falsely satisfy Codazzi.** [exceptional_initial.rs:122](/home/cosmosapjw/bass/_rustcore/src/geom/exceptional_initial.rs:122) checks only whether normalized `A` vanishes. Use `A=2^500`, `B=2^1020`, `C=3A`, `D=2^-100`, tolerance `2e-13`. Normalized `D` underflows to zero; construction accepts. `solve_transverse([0,0],1,1)` then returns shear `[0,1]` and zero residuals because lines 268–269 reuse the altered coefficients. The original transverse residual is `[-2^-100,0]`. Reject the lost nonzero coefficient.

- **P2 — Positive amplitude budget can permit no valid amplitude.** [exceptional_initial.rs:345](/home/cosmosapjw/bass/_rustcore/src/geom/exceptional_initial.rs:345) checks transverse constraints only at `χ=0`. With `(A,B,C,D,tolerance)=(1,0,3+1e-7,0,1e-6)`, zero in-plane shear/flux/density/Λ, and `κ=1`, `amplitude_budget(data,3)` returns approximately `14.9999994`. Passing either signed square root to `initial_data` fails the second Codazzi equation. Verify the returned amplitude against the full transverse constraints.

These are source-derived reproducers; I did not execute tests. The supplied PASS evidence does not cover these cases. Final validation and disposition remain with the parent.

Reviewed SHA-256 identities:

```text
exceptional_initial.rs
a8a82db99c3e8698fa981ef6a7ba5b9aa228570684fbc41048a14d768d921145
geom/mod.rs
b3851b96be2c3602134ac6014775e06a06af104d37fbbdf99f7d1933b7ca7d8e
exceptional_initial_contract.rs
fe9596e240456c0e8972b83b6c235d40a02b00ab70830f3faca46af4c791d996
EXCEPTIONAL_INITIAL_DATA_20260930.md
70b221068c3fdc1a55bed7f7b87c83dab09e94b9c7aeef96438a88f24e770426
contract.json
ff2ae264cc1d2a7b2c52b8fd3d7756dbdc22043f882a6ec42e
brief.md
1e06222d2e8507dd7f2354eb95b05db2e5641b855cacfc43176578d23dda7211
Dossier_I.txt (reviewed lines 270–438)
2d90cd5f7675aaeced17ceb577a658ff1931080a250b16c1587aad927ef26cd3
```
