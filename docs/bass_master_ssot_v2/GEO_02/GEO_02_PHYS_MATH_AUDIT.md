# GEO-02 PHYS–MATH audit

## Verdict

`PASS_SCOPED_LEVI_CIVITA_CONNECTION_AUTHORITY`

This verdict is limited to the spatial Levi–Civita connection generated from
the exact ALG-01R1 structure constants. Spatial curvature, Einstein equations
and background dynamics remain unadjudicated.

## Locked conventions

```text
metric signature        (-,+,+,+)
spatial metric          delta_alpha_beta
spatial orientation     epsilon_123=+1
commutator              [e_alpha,e_beta]=C^gamma_{alpha beta} e_gamma
connection              nabla_{e_alpha} e_beta
                        =Gamma^gamma_{alpha beta} e_gamma
array order             Gamma[[gamma,alpha,beta]]
rate dimension          [C]=[Gamma]=L^-1
natural units           not assumed
```

The parent algebra is

```text
C^gamma_{alpha beta}
 = epsilon_{alpha beta delta} n^{delta gamma}
 + a_alpha delta^gamma_beta
 - a_beta delta^gamma_alpha.
```

## Derivation

For the orthonormal spatial frame, the Koszul identity gives

```text
2 <nabla_{e_alpha} e_beta,e_gamma>
 = <[e_alpha,e_beta],e_gamma>
 - <[e_beta,e_gamma],e_alpha>
 + <[e_gamma,e_alpha],e_beta>.
```

Therefore

```text
Gamma^gamma_{alpha beta}
 = 1/2 (
     C^gamma_{alpha beta}
   - C^alpha_{beta gamma}
   + C^beta_{gamma alpha}
   ).
```

The torsion residual is

```text
T^gamma_{alpha beta}
 = Gamma^gamma_{alpha beta}
 - Gamma^gamma_{beta alpha}
 - C^gamma_{alpha beta}.
```

The metric-compatibility residual is

```text
M_{gamma alpha beta}
 = Gamma^gamma_{alpha beta}
 + Gamma^beta_{alpha gamma}.
```

Both vanish exactly for a general symbolic symmetric `n` and general symbolic
`a`. The Jacobi relation `n.a=0` is not required for this local connection
identity; it remains required for the input to define a Lie algebra.

## Uniqueness

Let `D^gamma_{alpha beta}` be the difference between two torsion-free,
metric-compatible connections on the same orthonormal frame. The homogeneous
conditions are

```text
D^gamma_{alpha beta}=D^gamma_{beta alpha},
D^gamma_{alpha beta}+D^beta_{alpha gamma}=0.
```

A Wolfram exact linear solve of 54 equations for all 27 components has one
solution and it is `D=0`. Thus the generated connection is unique.

## Canonical witness results

| Witness | nonzero `C` | nonzero `Gamma` | torsion | metric compatibility |
| --- | ---: | ---: | --- | --- |
| I | 0 | 0 | exact zero | exact zero |
| II | 2 | 6 | exact zero | exact zero |
| V | 4 | 4 | exact zero | exact zero |
| IX | 6 | 6 | exact zero | exact zero |
| exceptional VI_-1/9 | 6 | 10 | exact zero | exact zero |

For the canonical Type IX witness,

```text
Gamma^gamma_{alpha beta}=C^gamma_{alpha beta}/2.
```

The Type II and V component tables are checked exactly in the executable test.

## Frame covariance

For a constant orthogonal frame transformation `R`, the algebra data obey

```text
a' = R.a,
n' = det(R) R.n.Transpose[R].
```

The determinant is required because `n` is a spatial pseudotensor in the
locked decomposition. The structure constants and generated connection then
transform as true rank-three component arrays:

```text
Gamma'^gamma_{alpha beta}
 = R_{gamma rho} R_{alpha mu} R_{beta nu}
   Gamma^rho_{mu nu}.
```

Proper and improper transformations pass for Type II and exceptional
`VI_-1/9`. Omitting `det(R)` from the improper transformation of `n` produces
a nonzero connection residual and is detected.

## Dimension and limits

- `C`, `a`, `n`, `Gamma` and the connection one-form coefficients have
  dimension `L^-1` in the ray-length convention.
- Type I gives the exact zero spatial connection.
- The result is a spatial homogeneous-frame connection. It is not the full
  four-dimensional spacetime connection and contains no lapse, acceleration,
  expansion or shear time-connection components.
- No curvature or Einstein equation follows merely from passing this stage.

## Withheld conclusions

```text
NO_SPATIAL_CURVATURE_OR_RICCI_AUTHORITY
NO_HAMILTONIAN_OR_CODAZZI_AUTHORITY
NO_BACKGROUND_EVOLUTION_AUTHORITY
NO_CONSTRAINT_PROPAGATION_AUTHORITY
NO_ALL_FAMILY_RUNTIME_OR_SCIENCE_CLAIM
```
