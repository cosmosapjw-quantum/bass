# ALG-01R1 PHYS–MATH audit

**Stage:** `ALG_01R1`  
**Tested source:** `8b62a56a537e1a7f9f86d012e50f7161faa05b68`  
**Tested tree:** `c52f69b4f886efdb29d610b2de0eed3fe7f30971`  
**Verdict:** `PASS_SCOPED_ALGEBRA_WITNESS_CLOSEOUT`

## 1. Contract under audit

The locked Bianchi structure decomposition is

```text
C^gamma_{alpha beta}
 = epsilon_{alpha beta delta} n^{delta gamma}
 + a_alpha delta^gamma_beta
 - a_beta delta^gamma_alpha,

n^{alpha beta} a_beta = 0,
epsilon_123 = +1.
```

The exceptional `VI_-1/9` record is a dynamical sector of `VI_h`, not a
new public Bianchi algebra type. Its bounded witness uses

```text
a = (1,0,0),
n_perp = ((2,3),(3,0)),
Delta_N = -9,
h = -1/9,
Sigma_13 = 2,
Sigma_23 = 3.
```

## 2. Definition and scope consistency

PASS:

- `counted_public_algebra_type = false` is separated from
  `exceptional_sector = true`;
- the physical branch predicates contain the group and momentum constraints,
  but do not require every physical solution to have nonzero off-diagonal
  shear;
- `non_diagonal_shear_survival` is a **witness-only obligation** proving that
  the representation has not deleted the extra carrier;
- the canonical witness remains dimensionless and is not substituted for a
  physical rate or curvature magnitude.

This separation is load-bearing. Requiring `Sigma_13 != 0` or
`Sigma_23 != 0` as a physical branch predicate would incorrectly remove
admissible special submanifolds. Requiring the bounded witness to retain at
least one carrier is the correct regression contract.

## 3. Exceptional constraints and hostile deletion

For the canonical witness,

```text
9 A_1^2 - N_23^2 + N_22 N_33 = 0,
N_22 Sigma_12 + (N_23 - 3 A_1) Sigma_13 = 0,
h = A_1^2 / Delta_N = -1/9.
```

All exact residuals vanish. Replacing the shear by the zero matrix preserves
the algebra and exceptional constraints but violates the witness obligation.
The repaired validator therefore returns

```text
pass = false
failed_checks = {witness_obligations}
```

rather than falsely promoting the shear-deleted representation.

## 4. Proper and improper frame covariance

For exact `R in O(3)`, the project convention is

```text
a' = R a,
n' = det(R) R n R^T.
```

The generated structure constants satisfy

```text
C[a',n'] = R . C[a,n] . (R^T,R^T)
```

componentwise for both a proper cyclic rotation and an improper reflection,
for Type II and the exceptional witness. All four exact residual tensors
vanish.

A hostile mutation that transforms `n` as an ordinary tensor under the
improper reflection, omitting `det(R)`, gives structure-constant residual
L1 norm `4` and is detected.

## 5. Signs, units and limits

PASS:

- metric signature and orientation are unchanged;
- no new dimensional variable or natural-unit convention is introduced;
- the structure generator remains dimensionless at the witness level;
- Type I, II, V and IX witness classifications remain unchanged;
- non-orthogonal frame matrices fail closed rather than being interpreted as
  physical ONF changes.

## 6. Ranked audit ledger

| Rank | Finding | Disposition |
| --- | --- | --- |
| P0 | None in the scoped algebra/witness contract | PASS |
| P1 | Exceptional shear carrier could be deleted without failing the old validator | CLOSED by witness-only obligation and hostile mutation |
| P1 | Improper-frame pseudotensor sign was not machine-gated | CLOSED by exact O(3) covariance and sign mutation |
| P2 | Cartan connection and spatial curvature are not yet derived | WITHHELD; next DAG node |
| P2 | The five witnesses do not constitute all-family background support | WITHHELD |
| P3 | The CRAG figure is a diagnostic, not publication evidence | DISCLOSED |

## 7. Authorized and withheld claims

Authorized:

```text
ALG_01_BIANCHI_ALGEBRA_WITNESSES_VERIFIED
ALG_01_EXCEPTIONAL_SHEAR_AND_O3_COVARIANCE_VERIFIED
```

Withheld:

```text
CARTAN_CONNECTION_OR_CURVATURE_DERIVATION
BACKGROUND_EINSTEIN_MATTER_EQUATIONS
ALL_FAMILY_SOLVER_SUPPORT
GENERIC_ELL_COMPILER_CORRECTNESS
NUMERICAL_PARITY
CROSS_REPOSITORY_COMPATIBILITY
SCIENCE_VALIDITY
BASS_RF04_PROMOTION
```
