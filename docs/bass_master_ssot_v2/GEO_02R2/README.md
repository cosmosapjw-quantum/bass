# BASS Master SSOT v2 — GEO-02R2 composed connection stage

**Program ID:** `BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901`  
**Stage:** `GEO_02R2`  
**Canonical parent:** `ALG_01R2` commit `b0a2c8da9e74ce960394ae9c67c9744fb8e497ad`  
**Parent tree:** `da8a1de9a8432d8eaa43569c9637b8ce891e5daa`  
**Tested source commit:** `b93d3ddf82083c5afbe2e3a05ccc7c32c50e4eec`  
**Tested source tree:** `d56120cc41183ab7063fe4cd9399c88c1b13a21a`

## Purpose

This stage rebases and composes the previously sibling `GEO-02` spatial
connection generator onto the exact-identity `ALG-01R2` algebra/witness
parent. It is deliberately narrower than curvature or background evolution.

The generated array represents

```text
connection[[gamma, alpha, beta]]
  = Gamma^gamma_{alpha beta}
  = <e_gamma, nabla_{e_alpha} e_beta>.
```

For the locked structure constants,

```text
Gamma^gamma_{alpha beta}
 = 1/2 (
     C^gamma_{alpha beta}
     - C^alpha_{beta gamma}
     + C^beta_{gamma alpha}
   ).
```

The exact residual contracts are

```text
T^gamma_{alpha beta}
 = Gamma^gamma_{alpha beta}
   - Gamma^gamma_{beta alpha}
   - C^gamma_{alpha beta},

M^gamma_{alpha beta}
 = Gamma^gamma_{alpha beta}
   + Gamma^beta_{alpha gamma}.
```

They vanish for each declared sentinel witness.

## Index-order adapter

The generated tensor order and the locked project storage order are distinct:

```text
generated: {gamma, alpha, beta}
locked:    {alpha, beta, gamma}

locked[alpha,beta,gamma] = generated[gamma,alpha,beta]

generated -> locked: Transpose[..., {3,1,2}]
locked -> generated: Transpose[..., {2,3,1}]
```

An initial test contract used the reverse direct permutation. The
componentwise identity exposed the error, and the corrected test was replayed
against the unmodified `ALG-01R2` parent before the implementation was fixed.
The original candidate is preserved in the versioned Dropbox stage as an
adversarial failure witness.

## Exact witness results

| Key | Nonzero connection components | Exact sentinel statement |
|---|---:|---|
| I | 0 | zero spatial connection |
| II | 6 | exact half-integer connection table |
| V | 4 | pure Class-B vector connection |
| IX | 6 | `Gamma = C/2` for the unit isotropic witness |
| `VI_-1/9` | 10 | exceptional witness with independent `Sigma13`, `Sigma23` carriers preserved in the parent registry |

Proper and improper constant `O(3)` transformations pass when

```text
a' = R a,
n' = det(R) R n R^T.
```

The hostile mutation omitting `det(R)` is detected.

## Verification

```text
corrected focused composition test       18 / 18 PASS
GEO-02 donor + composition tests         33 / 33 PASS
full W0/W1 + ALG-01/R1/R2 + GEO-02 stack 114 / 114 PASS
failed                                    0
not evaluated                             0
```

Runtime authority:

```text
Wolfram 15.0.1 for Linux x86 (64-bit)
xAct/xTensor 1.3.0
xAct archive SHA-256
7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be

convention SHA-256
e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70

ALG-01R2 semantic registry SHA-256
e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762

connection module SHA-256
1f28c921734194c5a3b79e8d31ae045f7bfce336e2641e6e01a9232a0cdbc13d

test-stack SHA-256
02288d40138d362b6a57b72387b2608b342c42ffe2cccecebd04fbde631433e1
```

## Claim boundary

Authorized:

```text
GEO_02R2_LEVI_CIVITA_CONNECTION_COMPOSED_ON_ALG01R2
GEO_02R2_TORSION_METRIC_O3_INDEX_ORDER_VERIFIED
GEO_02R2_PARENT_IDENTITY_AND_EXCEPTIONAL_CARRIERS_PRESERVED
```

Withheld:

```text
SPATIAL_RIEMANN_RICCI_CURVATURE_DERIVATION
W2_GAUSS_CODAZZI_COMPOSITION
BACKGROUND_EINSTEIN_MATTER_EQUATIONS
CONSTRAINT_PROPAGATION
ALL_ELEVEN_BRANCH_BACKGROUND_SUPPORT
MATTER_EVOLUTION
GENERIC_ELL_COMPILER_CORRECTNESS
NUMERICAL_PARITY
CROSS_REPOSITORY_COMPATIBILITY
SCIENCE_VALIDITY
BASS_RF04_PROMOTION
```

## Next admissible work

The canonical line must next absorb the sibling W2 abstract 1+3/Gauss-Codazzi
sign registry or otherwise prove an exact compatible adapter, and then execute
`GEO_03` spatial Riemann/Ricci dual-oracle generation. `BG_02` Einstein
background constraints remain closed until those prerequisites are sealed.
