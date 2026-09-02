# SYNC-MAP-02B PHYS–MATH audit

## Scope

This audit classifies formula relations between the active BASS semantic export and the active `rec_bianchi` PR #47 lineage. It does not admit the REC physical directional face or provider, and it does not claim cross-repository semantic-hash equality for formulas absent from the BASS export.

## Locked conventions

- Metric signature: `(-,+,+,+)`.
- Spatial orientation: `epsilon_123=+1`.
- Photon direction: `p^a=(epsilon_gamma/c)(n^a+e^a)`.
- Observed output direction: `n_hat_obs^a=-e^a`.
- Physical ray-length parameter: `s=c t`.
- `H`, `sigma`, `a_B`, `n_B`, `Omega_triad`, and all characteristic rates have dimension `L^-1`.
- Lorentz velocity `beta`, gamma, the Doppler factor `D`, and Doppler-grid coordinate `x` are dimensionless.

## Formula checks

### Normal-frame photon energy drift

The REC occurrence and BASS owner expression are

```text
R_normal = -(H + e.sigma.e)
BASS R   = -H - e.sigma.e
```

Their exact symbolic residual is zero. Both sides have dimension `L^-1`.

### Normal-frame direction flow

After expanding REC's projected `spatial_term`, the exact residual against

```text
V = (e.sigma.e + a_B.e)e - sigma.e - a_B
    + Omega_triad cross e - e cross (n_B.e)
```

is `{0,0,0}`. The generated direction rate is tangent to the sphere:

```text
e.V = 0.
```

The formula has dimension `L^-1` and preserves `e.e=1` at the differential level.

### Doppler and aberration

For `0 <= beta^2 < 1`,

```text
D = gamma (1-beta.e) > 0.
```

The REC aberration formula produces a unit vector exactly. These formulas are therefore common BASS-owned frame relations in this program, not REC-owned new derivations.

### Hydrogen-frame specialization

REC owns the specialization

```text
R_H = R_normal + D0 ln D.
```

This is an adapter from the common normal-frame photon characteristic to the hydrogen rest frame. It is not a competing owner of the normal-frame drift or Lorentz transformation.

### Moving Doppler face

REC owns

```text
v_x = [nu_face R_H - D0 nu_abs]/Delta_nu_D
      - x D0 ln Delta_nu_D - D0 x_face.
```

Every term has dimension `L^-1`. Direct differentiation of the moving coordinate gives exact residual zero.

The events `R_H=0`, `v_x(red)=0`, and `v_x(blue)=0` are not interchangeable. Exact counterexamples give:

```text
R_H=0 but v_x=-1,
v_x=0 while R_H=1.
```

Therefore the three event surfaces must remain distinct.

## Known limits and domains

- `beta -> 0`: `D -> 1` and the hydrogen direction approaches the normal-frame direction.
- Isotropic/shear-free normal-frame limit: `R_normal -> -H`.
- Static frequency grid: the moving-grid terms reduce but do not identify `R_H=0` with face grazing.
- The relation audit assumes positive Doppler width `Delta_nu_D>0`.
- No claim is made outside the active REC PR #47 lineage or for historical branches.

## Ranked findings

### P0

None.

### P1

1. Four common BASS formulas are not yet present in the fourteen-formula canonical EquationIR export:
   - `BASS.FRAME.ABERRATED_DIRECTION.001`;
   - `BASS.FRAME.DOPPLER_FACTOR.001`;
   - `BASS.PHOTON.DIRECTION_FLOW.001`;
   - `BASS.PHOTON.ENERGY_DRIFT.001`.

   Exact algebraic residuals support compatibility, but cross-repository semantic identity remains unpromoted until those owner records exist.

2. The source-defined physical 26-direction face is still absent. Consequently `REC.PROVIDER_EXPORT` remains blocked by `NO_PASS_REC_PHYSICAL_SPLIT`.

### P2

1. The mixed REC Wolfram script contains ten common frame checks and nineteen REC-owned face/microphysics checks. It must be treated as a split, authority-effect-`NONE` oracle rather than a second formula authority.
2. The BASS-14 comparison covers the active REC lineage only; it is not a historical all-branch duplicate scan.

### P3

- The literature search is methodological support only and does not establish project-local source identity or implementation use.

## Verdict

```text
PASS_REC_RELATION_CLASSIFICATION
WITH_FOUR_OWNER_EXPORT_GAPS
AND_REC_PHYSICAL_FACE_BLOCKER_PRESERVED
```

No formula inconsistency was found in the bounded shared relations. The remaining load-bearing problem is authority completion, not an observed sign, normalization, or dimensional mismatch.
