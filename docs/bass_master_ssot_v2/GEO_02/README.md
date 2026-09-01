# BASS Master SSOT v2 — GEO-02 Levi–Civita Connection Generator

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `GEO_02`  
**Exact parent:** `research/bass-master-ssot-v2-alg01-20260901-r1@24e8d5ae3b7e929e34ca62d7070ce00e0960fb46`  
**Parent tree:** `a0f8cab48cdb32c18282d512f2b2ecb45083b62d`  
**Jira owner:** `BASS-17`

## Scope

GEO-02 lowers the ALG-01 Bianchi structure constants to the unique torsion-free,
metric-compatible spatial connection in the locked orthonormal frame. It adds:

- the exact Koszul connection generator;
- torsion and metric-compatibility residuals;
- sparse connection one-form terms;
- constant proper/improper `O(3)` covariance;
- canonical witness checks for I, II, V, IX and exceptional `VI_{-1/9}`;
- a hostile missing-`det(R)` parity mutation.

It does **not** derive spatial curvature, Ricci tensors, Einstein equations,
matter evolution, constraint propagation, numerical trajectories or the
arbitrary-ell compiler.

## Convention and formula

The parent stage defines

```text
[e_alpha,e_beta] = C^gamma_{alpha beta} e_gamma,
C^gamma_{alpha beta}
 = epsilon_{alpha beta delta} n^{delta gamma}
 + a_alpha delta^gamma_beta
 - a_beta delta^gamma_alpha,
epsilon_123 = +1.
```

For the orthonormal spatial metric `delta_{alpha beta}`, GEO-02 defines

```text
Gamma^gamma_{alpha beta}
 = 1/2 (
     C^gamma_{alpha beta}
   - C^alpha_{beta gamma}
   + C^beta_{gamma alpha}
   ).
```

The generated residuals are

```text
T^gamma_{alpha beta}
 = Gamma^gamma_{alpha beta}
 - Gamma^gamma_{beta alpha}
 - C^gamma_{alpha beta},

M_{gamma alpha beta}
 = Gamma^gamma_{alpha beta}
 + Gamma^beta_{alpha gamma}.
```

Both vanish exactly. Since `[C]=L^-1`, the connection also has
`[Gamma]=L^-1`; no natural-unit substitution is made.

## Verification

TDD RED was observed against the exact ALG-01R1 restore source for five absent
public APIs. A first implementation replay produced `6 PASS / 9 FAIL` because a
line-leading `&&` was rejected by the Wolfram parser. A syntax-only `And[...]`
repair preserved every formula and coefficient.

After repair:

```text
focused GEO-02 tests       15 PASS / 0 FAIL / 0 NOT_EVALUATED
full W0/W1+ALG+GEO stack   78 PASS / 0 FAIL / 0 NOT_EVALUATED
xAct/xTensor               1.3.0 loaded
manifold/CovD/Riemann      PASS / PASS / PASS
```

Connection and one-form nonzero counts are

```text
I           0
II          6
V           4
IX          6
VI_-1/9    10
```

A separate generic symbolic oracle verifies exact torsion and metric residuals
for general symbolic symmetric `n_{alpha beta}` and general `a_alpha`. The 54
homogeneous equations for the difference of two admissible connections have a
single solution: all 27 difference components vanish. This uniqueness proof
does not require the Jacobi constraint.

## Run

```bash
wolframscript -file wolfram/scripts/run_stage.wls --stage GEO_02
```

A local exact-pinned xAct archive may be supplied with `--xact-source`.

## Claim ceiling

```text
GEO_02_LEVI_CIVITA_CONNECTION_WITNESSES_VERIFIED
GEO_02_TORSION_METRIC_AND_O3_COVARIANCE_VERIFIED
NO_SPATIAL_CURVATURE_OR_RICCI_DERIVATION
NO_BACKGROUND_EINSTEIN_MATTER_EQUATIONS
NO_CONSTRAINT_PROPAGATION
NO_ALL_FAMILY_SOLVER_SUPPORT
NO_GENERIC_ELL_COMPILER_CORRECTNESS
NO_NUMERICAL_OR_SCIENCE_PROMOTION
NO_PASS_RF04
```
