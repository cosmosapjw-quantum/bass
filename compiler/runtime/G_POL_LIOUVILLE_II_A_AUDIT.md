# G-POL-LIOUVILLE-II-A hostile audit

## Verdict

**PASS as a Type-II ray-level polarized Liouville characteristic authority
lane.**  This is subgate A of `G-POL-LIOUVILLE-II`; the full node remains open.

The strongest allowed claim is:

> Hubble-normalized Type-II collisionless polarized ray characteristic with
> basis-free physical-screen tensor transport by a second-order Lie-midpoint
> SO(3) congruence.

## Physical contract

With signature `(-,+,+,+)` and the project photon direction `e`, the implemented
homogeneous coefficients are

```
d ln epsilon/dlambda = -(H + sigma_ab e^a e^b),

e_dot = -sigma.e + sigma_ee e
        - a + (a.e)e - e x(n.e) + Omega x e,

W = Omega + a x e + n.e - tr(n)e/2,
omega_scr = e.W.
```

Writing `v_sigma=-sigma.e+sigma_ee e`, the code forms

```
g = W + e x v_sigma,
e_dot = g x e.
```

For the bolometric coherency tensor `J`,

```
J_dot = 4(d ln epsilon/dlambda) J + [g x]J + J[g x]^T.
```

The factor four is the bolometric redshift weight.  This checkpoint does not
claim the spectral `-3R` distribution equation.

## Type-II adapter

For `X=(Sigma_+,Sigma_-,Sigma_13,N1,v2)` the H-normalized adapter uses

```
sigma = [[-2 Sigma_+, 0, sqrt(3) Sigma_13],
         [0, Sigma_+ + sqrt(3) Sigma_-, 0],
         [sqrt(3) Sigma_13, 0, Sigma_+ - sqrt(3) Sigma_-]],

n = diag(N1,0,0),
Omega = (0,sqrt(3) Sigma_13,0),
H = 1.
```

`v2` remains a collision/global-electron state and is deliberately absent from
geometric Liouville coefficients.  At `N1=0`, the diagonal-`n` eigenframe is
degenerate.  The adapter accepts the regular `Sigma_13=0` boundary and rejects a
nonzero off-diagonal shear unless a separate gauge is supplied.

## Numerical method

Each substep evaluates the midpoint background and solves

```
e_mid = exp[(h/2) [g(e_mid) x]] e_n
```

by fixed point.  It then applies

```
R = exp[h [g(e_mid) x]],
e_{n+1}=R e_n,
J_{n+1}=exp(4 Delta ln epsilon) R J_n R^T.
```

This retains the SO(3) action, screen transversality and coherency-cone
congruence instead of projecting a generic additive update after the fact.

## Equation-to-code map

- general coefficients: `liouville_coefficients`;
- Type-II chart: `typeii_background_from_state`;
- instantaneous tensor equation: `polarized_bolometric_rhs`;
- arbitrary background profile: `transport_characteristic_profile`;
- endpoint-linear profile: `transport_characteristic`;
- generated Type-II endpoint adapter: `transport_typeii_characteristic`;
- physical carrier: inherited `typeii_physical_guard`;
- convergence figures: `plot_typeii_polarized_liouville.py`, reading the machine receipt rather than test stdout.

## Independent validation

### Direct formula route

Six Python tests do not import the Rust implementation.  They check the full
homogeneous direction flow, `g x e`, screen-constraint derivative, trace of the
rotation part, omitted-twist negative control, Type-II adapter, and a direct
Ricci-rotation-coefficient construction.

### Coordinate Bianchi-II route

An independent coordinate metric

```
ds^2=-dt^2+a1(t)^2(dx-N1 y dz)^2+a2(t)^2dy^2+a3(t)^2dz^2
```

is integrated through its metric Christoffel symbols, transporting a null
momentum and two coordinate four-vectors.  It agrees with a separately written
tetrad formula route to

- direction max error `3.89e-16`;
- log-energy error `1.53e-16`;
- spatial-transport max error `4.93e-16`;
- null residual `-3.03e-16`.

The Rust 4096-substep result agrees with the coordinate oracle within the public
`3e-10`/`5e-11` tolerances and reports SO(3) defects below `2e-13`.

### Rust structure and limit gates

The 16-test unit suite covers:

- FLRW bolometric scaling;
- Minkowski identity;
- pure screen twist with fixed direction;
- instantaneous tensor RHS;
- Type-II authority formulas;
- global tilt exclusion from geometry;
- physical screen/cone and V=0 preservation;
- self-adjoint forward/backward roundtrip;
- second-order time dependence;
- fail-closed invalid input;
- trace-rate invariance;
- proper-frame covariance;
- Type-I gauge degeneration;
- coordinate-oracle parity;
- exact diagonal Bianchi-I tetrad-momentum direction/redshift recovery;
- invalid direction and non-symmetric/non-tracefree geometric background fail-closed gates.

Measured generic refinement errors for substeps `4,8,16,32` are

```
3.2708027418631991e-4,
8.1715645555785477e-5,
2.0425440581312015e-5,
5.1060882124143170e-6,
```

with ratios `4.0026640, 4.0006797, 4.0002130`.

Forward/backward roundtrip defects are

- direction `1.05e-15`;
- coherency `2.55e-15`;
- log energy `5.55e-17`.

### Source-derived Type-II trajectory

The existing 401-sample source trajectory is replayed interval by interval.  Its
substeps-per-interval `1,2,4,8` errors against 16 are

```
6.6867411607773874e-10,
1.6520573797862426e-10,
3.9338809987299328e-11,
7.8692052873918783e-12,
```

with ratios `4.0475, 4.1996, 4.9991`.  The coarsest lane reports

- log-energy shift `-0.21063405481614572`;
- screen-connection integral `-0.05150824491471552`;
- max screen leakage `2.22e-16`;
- minimum coherency eigenvalue `0.14577045446371167`.

The last ratio is mild superconvergence relative to the finest in-sample
reference and is not promoted to an order greater than two.

## Fresh software replay

Pinned environment:

- Rust `1.94.1 (e408947bf 2026-03-25)`;
- Cargo `1.94.1 (29ea6fb6a 2026-03-24)`;
- `Cargo.lock` SHA-256
  `d500208e9353ade1cb74693918598846628219e6e7bd2e2bce9ec85e29eb6310`.

Fresh results:

- full locked/offline RustCore: **218/218** tests;
- new Rust Liouville tests: **17/17** (16 unit + 1 source fixture);
- independent Python validation: **6/6**;
- changed-file rustfmt: PASS;
- receipt-driven convergence plot regeneration: PASS;
- no warning names a new Liouville source/test; emitted warnings are inherited
  RustCore warnings.

## Plot-driven CRAG reading

The generic convergence plot lies on the second-order reference over every
resolution.  The source-trajectory plot also follows the second-order reference;
the finest point falls below it, so the claim remains second order rather than
being inflated to superconvergence.

Adversarial mutations already retained in tests:

- omit screen twist;
- put global electron tilt into geometric transport;
- use additive tensor stepping instead of SO(3) congruence;
- continue the exact Type-I boundary in the singular diagonal gauge;
- rotate the frame without rotating all inputs and outputs.

All are detected or fail closed.

## Risk ledger

### P0

None found within the stated ray-level scope.

### P1

None found within the stated ray-level scope.

### P2

1. `screen_connection_integral` is diagnostic only.  The active/passive
   component sign of the future Q/U adapter is intentionally not sealed here.
2. No angular remap exists.  A collection of independent characteristics is not
   yet a fixed-grid Liouville solver.
3. Collision, Kato and AP policies are not composed with this characteristic.
4. The Type-II adapter is H-normalized and branch-specific; cross-family support
   requires a distinct authority mapping.

## Claim boundary

Not claimed:

- full `G-POL-LIOUVILLE-II` closure;
- a fixed-grid or semi-Lagrangian angular solver;
- sign-locked Q/U, E/B or Wigner transport;
- collision + Kato + Liouville integration;
- observer/local-boost outputs;
- PSTF/harmonic outputs;
- cross-family or production migration;
- observables/statistics readiness.

## Next DAG node

`G-POL-LIOUVILLE-II-B`: seal the finite tensor-to-dyad/Stokes adapter and its
active/passive sign, then build a screen-aware angular remap with forward/backward
and quadrature-refinement tests.  Only after B should node C compose Liouville,
collision, Kato and raw/AP policies on the source-derived Type-II trajectory.
