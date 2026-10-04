# Cold-Thomson energy-validity and consumer contract

Status: `BOUNDED IMPLEMENTATION — INSTANTANEOUS — NOT PRODUCTION WIRED`  
Date: 2026-08-23

## Scope and conventions

The metric is `(-,+,+,+)`.  Photon energy is in joules, electron temperature
is in kelvin, and `c`, `k_B`, and `m_e c^2` remain explicit.  The public
constant owner is `bianchi.physical.units`, using exact SI `k_B` and the CODATA
2022 electron rest energy.

For a photon energy upper bound in a named source observer,

\[
x_{\max}=\frac{D_{\max}E_{s,\max}}{m_ec^2},\qquad
\theta_e=\frac{k_BT_e}{m_ec^2}.
\]

For the source/electron relative observers,

\[
\Gamma_{se}=\frac{1-\boldsymbol\beta_s\!\cdot\!\boldsymbol\beta_e}
 {\sqrt{(1-\beta_s^2)(1-\beta_e^2)}},\qquad
D_{\max}=\Gamma_{se}+\sqrt{\Gamma_{se}^2-1},\quad
D_{\min}=D_{\max}^{-1}.
\]

These are the exact extrema over the full source-frame unit sphere.  They are
conservative if the actual angular support is restricted.

## Total Klein–Nishina rate authority

With `x=E_e/(m_e c^2)`, the stationary-electron total cross-section ratio is

\[
\frac{\sigma_{KN}}{\sigma_T}=\frac34\left[
\frac{1+x}{x^3}\left(\frac{2x(1+x)}{1+2x}-\ln(1+2x)\right)
+\frac{\ln(1+2x)}{2x}-\frac{1+3x}{(1+2x)^2}\right].
\]

The implementation uses a Wolfram-derived series through `x^10` for
`x<=10^-3` and a portable stdlib Decimal-80 evaluation above it:

\[
1-2x+\frac{26}{5}x^2-\frac{133}{10}x^3+\cdots.
\]

The total-cross-section deficit is evaluated directly, rather than subtracting
the rounded ratio from one, so `x=10^-20` remains positive and cannot pass a
zero budget.  The measure is explicitly `(sigma_T-sigma_KN)/sigma_T`.  A
caller-owned budget is hash-pinned, but it is not a global project ceiling.
The generic `valid_for_requested_budget` flag is true only for a completed
exact-cold certificate; finite-temperature diagnostic predicates have their
own `declared_scalar_predicates_pass` field.

Primary sources:

- Klein–Nishina original result: https://doi.org/10.1007/BF01366453
- Modern exact LO formula and threshold expansion:
  https://arxiv.org/abs/2102.06718
- CODATA 2022 constants:
  https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958143

## Fail-closed boundaries

Only `HARD_FINITE` energy support can close this gate.  `BOLOMETRIC`,
`UNKNOWN`, and `EFFECTIVE_TAIL` return `UNVERIFIED_ENERGY_SUPPORT`.  In
particular, Mode A is bolometric, while Mode B's finite `ln q` grid has no
physical J/eV calibration and does not prove a hard spectral cutoff.

The total cross section is not a polarized differential-kernel bound.  A
positive temperature has an unbounded thermal momentum tail; therefore
`theta_e <= theta_max` is recorded as a diagnostic policy but does not certify
finite-temperature redistribution.  Without a separately normalized tail and
operator-error authority, `T_e>0` returns
`UNVERIFIED_FINITE_TEMPERATURE_TAIL`.  Sazonov–Sunyaev's thermal Compton kernel
likewise treats photon energy and temperature as distinct expansion
parameters: https://arxiv.org/abs/astro-ph/9910280

At `n_e*=0`, the result is `VACUOUS_COLLISION_OFF`, never a Thomson-domain
pass.  Each non-vacuum certificate is instantaneous at the declared `event_id`.
It cannot be reused along a Bianchi trajectory without a joint time-aligned
spectral/electron/temperature authority and a segment supremum.

Every certificate binds length-prefixed canonical hashes for the hard energy
bound, source observer frame, electron state, electron temperature, requested
budget, constants profile, measured outputs, and status.  All four physical
inputs must carry the same `event_id`, and the bound's `source_frame` must
equal the observer authority's `frame_id`.  Signed zero is canonicalized and
embedded NUL is rejected in free identifiers.  Relative gamma and one-ray
Doppler factors treat the supplied binary64 components as exact values and use
Decimal precision 80; accepted near-unit directions are normalized before the
one-ray factor is evaluated.

## Exactly one relative-flux factor

The two classified outputs are distinct types:

```text
RestOpacityPerSecond       n_e* sigma_T c
ObserverRayRatePerSecond   n_e* sigma_T c D_e<-source
```

The frozen consumer ID
`bianchi.matter.collision_moving.collision_rate_density` applies `D=lp/L`
itself and is mapped to rest opacity.  The external single-observer-ray ID is
mapped to the observer rate.  Passing the wrong typed value to the bounded
validator is rejected; production runtime signatures still accept naked
scalars, so enforcement outside this authority remains explicitly false.

The current scalar Q collision path is not declared compatible with either
shortcut.  Its source-time generator contains `M_D(K-I)`, and multiplication
by direction-dependent `D` does not commute with Thomson scattering `K`.  For
`D=gamma(1-beta mu)`, `K 1=1` and `K D=gamma`, so

\[
(M_DK-KM_D)1=-\gamma\beta\mu\ne0.
\]

It is therefore blocked as `SCALAR_Q_KERNEL_UNRESOLVED` until a separately
derived direction-dependent generator is implemented and tested.

This module returns a positive local future-ray rate.  Backward kinetic IVP
evolution versus past-directed optical-depth accumulation, reverse schedule
support, and signed integration orientation remain unverified and must not be
inferred from the local rate.

## Deliberate stop boundary

No `Collision.v_b`, solver loop, JAX/Rust ABI, finite-ell carrier,
projector/classifier, branch, commit, PR, Jira, or Confluence wiring is part of
this authority.  No authority row is promoted.
