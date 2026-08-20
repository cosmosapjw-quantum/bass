# G-POL-LIOUVILLE-IIA Design

## Purpose

Build a narrow Type-II paired-characteristic authority lane for collisionless polarized Liouville transport. The lane advances a photon direction, bolometric energy weight, and the physical screen coherency tensor. It does not perform fixed-grid angular remapping, PSTF/harmonic projection, collision composition, observer boosting, or observable generation.

## Conventions

- Metric signature: `(-,+,+,+)`.
- Tetrad commutator: `[e_b,e_c]=C^a_{bc}e_a`.
- Hubble-normalized Type-II evolution parameter: all geometric rates are divided by `H`, so `expansion=1`.
- Type-II state: `(Sigma_+,Sigma_-,Sigma_13,N1,v2)`.
- Shear tensor:
  `diag(-2 Sigma_+, Sigma_+ + sqrt(3) Sigma_-, Sigma_+ - sqrt(3) Sigma_-)`
  with `sigma_13=sqrt(3) Sigma_13`.
- Diagonal-`N` frame adapter: `R=(0,sqrt(3) Sigma_13,0)`.
- `v2` is a global electron/collision variable and does not enter geometric Liouville transport.
- The stored tensor has nine real components, while checked physics is restricted to the four-real-dimensional screen carrier `J=P(e)JP(e)`.
- Bolometric brightness scales as `p^4`, hence `d ln J/dtau = 4 d ln p/dtau` apart from screen rotation.

## Authority equations

For unit direction `e`, symmetric shear `sigma`, class-B vector `A`, symmetric structure tensor `N`, and tetrad rotation `R`,

```
d ln p/dtau = -(1 + sigma_ab e^a e^b)

de/dtau = -(sigma e - (e.sigma.e)e)
          + R x e + (N e) x e - (A-(A.e)e).
```

Define

```
w = R + A x e + N e - 0.5 tr(N)e
v_sigma = -sigma e + (e.sigma.e)e
Omega = w + e x v_sigma.
```

Then `de/dtau = Omega x e`, and the physical screen vector/tensor transport generated from the Ricci rotation coefficients is

```
dW/dtau = Omega x W,
dJ/dtau = [Omega]_x J + J [Omega]_x^T + 4(d ln p/dtau)J.
```

The component parallel to `e`, `omega_scr=e.w`, is retained as a gauge/adapter diagnostic. Quantitative global E/B projection is outside this slice.

## Numerical method

Each substep freezes the linearly or callback-supplied background at its temporal midpoint. The midpoint direction solves the Lie-group fixed point

```
e_m = exp((h/2)[Omega(e_m)]_x)e_n.
```

The accepted update is

```
e_{n+1}=exp(h[Omega(e_m)]_x)e_n,
J_{n+1}=exp(4 h dlnp_m) R_m J_n R_m^T.
```

This preserves unit direction, screen congruence, cone eigenvalues up to the positive scalar weight, and is self-adjoint when the background path is reversed. Fixed-point failure is explicit and fail-closed.

## Interfaces

- `typeii_background_from_state`: generated Type-II chart to geometric coefficients.
- `liouville_coefficients`: instantaneous direction/redshift/screen generator.
- `polarized_bolometric_rhs`: checked instantaneous tensor RHS.
- `transport_characteristic_profile`: arbitrary deterministic midpoint background profile on a single step.
- `transport_characteristic`: endpoint-linear convenience wrapper.
- `transport_typeii_characteristic`: endpoint-linear Type-II state wrapper.
- Result includes final direction/coherency, energy and bolometric shifts, integrated screen connection, cumulative proper rotation, orthogonality/determinant diagnostics, screen leakage, and cone margin.

## Validation gates

1. Minkowski and FLRW limits.
2. Pure tetrad rotation about a fixed ray: `I,V` invariant and linear polarization rotates with spin two.
3. Direct Ricci-rotation-coefficient oracle for direction and screen-vector rates.
4. Constant diagonal Bianchi-I analytic momentum/redshift limit.
5. Independent coordinate Bianchi-II oracle for direction, redshift, and cumulative screen rotation.
6. Type-II adapter formula and explicit global-tilt exclusion.
7. Instantaneous RHS central difference.
8. Frame covariance under a proper spatial rotation.
9. Forward/backward roundtrip.
10. Second-order convergence for time-dependent background interpolation.
11. Source-derived Type-II trajectory screen/cone preservation.
12. Invalid carrier, direction, background, step, and midpoint convergence fail closed.

## Claim boundary

Allowed: `Type-II paired-ray polarized geometric/free-streaming Liouville reference lane with first-principles screen transport and independent coordinate oracle`.

Not allowed: fixed-grid collocation accuracy, harmonic/PSTF E/B hierarchy, collision-plus-Liouville production splitting, line-of-sight observables, local observer boost, cross-family support, statistics readiness, or production migration.
