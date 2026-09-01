# W3 — ONF Levi–Civita Connection and Curvature Witnesses

**Program:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `W3`  
**Canonical parent:** ALG-01 R1 at `24e8d5ae3b7e929e34ca62d7070ce00e0960fb46`  
**Tested source:** `5d3e8ecce2a40a1bc2b43af7daa985e042d9815f` / tree `0fee5b6335a2eb8968c11790ce787bf54fdc1def`  
**Status:** `SYMBOLIC_VERIFIED_WITH_I_V_IX_COMPONENT_WITNESSES`

## Scope

W3 adds the exact homogeneous orthonormal-frame Levi–Civita connection and
spatial curvature generators downstream of ALG-01 and W2. It validates three
discriminating witnesses:

- Bianchi I: flat Class A;
- Bianchi V: negatively curved Class B;
- Bianchi IX: positively curved full-rank Class A.

The direct ONF formula is checked against an independent xCoba coordinate
metric calculation followed by exact tetrad pullback of the complete
`3 x 3 x 3 x 3` Riemann component array.

## Locked formulas

With

```text
Gamma_{alpha beta gamma} = <e_gamma, nabla_{e_alpha} e_beta>,
```

torsion freedom and metric compatibility give

```text
Gamma_{alpha beta gamma}
 = 1/2 (C_{gamma alpha beta}
       - C_{alpha beta gamma}
       + C_{beta gamma alpha}).
```

For spatially homogeneous frame coefficients,

```text
R_{alpha beta gamma delta}
 = Gamma_{beta gamma mu} Gamma_{alpha mu delta}
 - Gamma_{alpha gamma mu} Gamma_{beta mu delta}
 - C^mu_{alpha beta} Gamma_{mu gamma delta}.
```

The contractions are

```text
R_{gamma beta} = sum_alpha R_{alpha beta gamma alpha},
R = delta^{gamma beta} R_{gamma beta}.
```

Dimensions:

```text
[C] = [Gamma] = L^-1,
[Riemann] = [Ricci] = [R] = L^-2.
```

## Exact witness values

| Type | Ricci tensor | Scalar curvature | `R_1221` |
| --- | --- | ---: | ---: |
| I | `0` | `0` | `0` |
| V | `-2 I_3` | `-6` | `-1` |
| IX | `(1/2) I_3` | `3/2` | `1/4` |

The xAct all-lower coordinate Riemann is mapped to the locked BASS convention
with one explicit overall minus sign before tetrad pullback.

## Verification history

The history is failure-preserving:

```text
TDD RED:             0/4 expected APIs present
Initial restored run: 3/15 PASS, 12/15 FAIL
Fix 1 restored run:  14/15 PASS, 1/15 FAIL
Final restored run:  15/15 PASS
```

The first failure was caused by xCoba component materialization and package
namespace handling, plus association aggregation over keys. The second was a
validator-only use of an undefined `RationalQ`; it was replaced by
`MatchQ[x,_Rational]`. Neither repair changed a geometric formula, metric,
tetrad, curvature expectation, or Riemann sign adapter.

## Backup

Canonical non-overwriting Dropbox path:

```text
/bianchi/bass/backups/BASS-MASTER-SSOT-V2/2026-09-02/W3_AFTER_ALG01R1_W2
```

Restore layering:

```text
parent_W0_W1
→ parent_ALG_01R1
→ sources
→ fix1
→ fix2
```

## Next stage

W4/BG-02 begins from the abstract Einstein residual

```text
E_ab = G_ab + Lambda g_ab - (8 pi G/c^4) T_ab
```

and generates Hamiltonian, momentum, spatial-trace, and spatial-PSTF
projections. W4 remains RED in this stage.

## Claim boundary

Authorized:

```text
W3_ONF_CONNECTION_CURVATURE_FORMULAS_VERIFIED
W3_I_V_IX_XCOBA_FULL_RIEMANN_WITNESSES_VERIFIED
DROPBOX_W3_EXACT_TEXT_RESTORE_15_OF_15_PASS
```

Withheld:

```text
ALL_TYPE_CURVATURE_SPECIALIZATION
BACKGROUND_EINSTEIN_MATTER_EVOLUTION
ALL_FAMILY_SOLVER_SUPPORT
GENERIC_ELL_COMPILER_CORRECTNESS
NUMERICAL_PARITY
CROSS_REPOSITORY_COMPATIBILITY
SCIENCE_VALIDITY
BASS_RF04_PROMOTION
```
