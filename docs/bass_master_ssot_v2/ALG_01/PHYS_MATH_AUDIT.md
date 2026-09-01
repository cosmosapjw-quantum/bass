# ALG-01 PHYS–MATH AUDIT

**Verdict:** `PASS_WITH_STRICT_ALGEBRA_SCOPE`  
**Tested source commit/tree:** `be30f27acbe9c8be66aaa1e0831ab6f7cb158294` / `fe389bce6ddbaaabc957651a014b4f319d998ebe`

## 1. Locked definitions

The stage uses

```text
C^gamma_{alpha beta}
 = epsilon_{alpha beta delta} n^{delta gamma}
 + a_alpha delta^gamma_beta
 - a_beta delta^gamma_alpha,

epsilon_123 = +1,
n^{alpha beta} = n^{beta alpha}.
```

The vector Jacobi residual is `n.a`. The independent full residual is

```text
J^delta_{alpha beta gamma}
 = C^mu_{beta gamma} C^delta_{alpha mu}
 + C^mu_{gamma alpha} C^delta_{beta mu}
 + C^mu_{alpha beta} C^delta_{gamma mu}.
```

The coframe convention is

```text
d omega^gamma
 = -(1/2) C^gamma_{alpha beta}
   omega^alpha wedge omega^beta.
```

For `alpha<beta`, the displayed wedge coefficient is therefore
`-C^gamma_{alpha beta}`.

## 2. Definition and sign checks

| Check | Result |
| --- | --- |
| metric/orientation inherited from W1 | PASS: `(-,+,+,+)`, `epsilon_123=+1` |
| lower-index antisymmetry of `C` | PASS for all five witnesses |
| vector Jacobi residual `n.a` | exact zero for all five witnesses |
| full tensor Jacobi residual | exact zero for all five witnesses |
| Cartan-to-structure reconstruction | exact identity for all five witnesses |
| invalid input | fail-closed `Failure` |

The vector and full-tensor Jacobi checks are intentionally retained as
independent representations. A hostile `a=(1,0,0), n=IdentityMatrix[3]`
mutation produces `n.a={1,0,0}` and six nonzero full Jacobi components.

## 3. Dimensional and gauge firewall

The canonical witnesses are explicitly tagged

```text
dimensionless canonical algebra witness only
```

and are rejected if relabelled as physical magnitudes. This prevents the
integer/rational fingerprints from being substituted for dimensional physical
ONF variables. Later physical `a_alpha`, `n_{alpha beta}`, `H_geom`, shear and
triad-rotation rates remain `L^-1` quantities.

Temporal triad rotation is retained by the type specification. No optional
Fermi-propagated temporal gauge is silently promoted to the authority gauge.

## 4. Witness results

| Witness | Rank/inertia | Special condition | Result |
| --- | --- | --- | --- |
| I | rank 0, `(0,0,3)` | `a=0`, `n=0` | PASS |
| II | rank 1, `(1,0,2)` | Class A | PASS |
| V | rank 0, `(0,0,3)` | Class B, `a!=0`, `n=0` | PASS |
| IX | rank 3, `(3,0,0)` | same-sign inertia | PASS |
| VI_-1/9 | rank 2, `(1,1,1)` | `det(n_perp)<0`, `h=-1/9` | PASS |

For the exceptional witness,

```text
9 A_1^2 + det(n_perp) = 0,
N_22 Sigma_12 + (N_23-3A_1) Sigma_13 = 0,
h = -1/9.
```

The chosen witness keeps nonzero `Sigma_13` and `Sigma_23`; it does not
replace the full exceptional constraint surface by a diagonal-shear subset.

## 5. Known limits and counterexamples

- I is the exact zero-structure limit.
- V isolates the Class-B vector channel with vanishing `n`.
- IX tests a full-rank same-sign Class-A carrier.
- VI_-1/9 tests the exceptional dynamical sector, not a twelfth algebra type.
- Sign/rank-only mutation of IX is rejected even though the Jacobi identity
  remains satisfied; Jacobi validity alone is therefore not mistaken for
  branch identity.
- Exceptional `h` and exceptional momentum mutations are independently
  rejected.

## 6. Ranked findings

### P0

None within the declared ALG-01 scope.

### P1

- Cartan connection, curvature, Einstein equations and constraint propagation
  are not derived. Any background-ready claim is forbidden.

### P2

- The witness set is deliberately five-branch and cannot establish an
  eleven-family generator by itself.
- No independent xCoba component-frame curvature oracle exists yet; it belongs
  to the next geometry node.
- Exact inertia evaluation is admitted for exact decidable matrices only;
  unresolved symbolic inertia must remain fail-closed.

### P3

- The CRAG chart counts failed contracts; it is a diagnostic visualization,
  not a physical norm or observable.

## 7. Authorized claim

```text
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED
```

This audit does not authorize curvature, background evolution, family-wide
solver support, numerical parity, observables, statistics or RF04 promotion.
