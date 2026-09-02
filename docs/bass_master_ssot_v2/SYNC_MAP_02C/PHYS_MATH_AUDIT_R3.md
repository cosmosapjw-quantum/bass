# PHYS–MATH audit — SYNC-MAP-02C R3

## Disposition

`PASS_COMPLETE_ACTIVE_REI_SOURCE_MATRIX_WITH_SCOPE_BOUNDARIES`

This audit covers relation ownership, the complete 22-path active REI source
matrix and the six-record REC+REI+HTT shared-formula union. It does not promote
an implementation or provider.

## Conventions and dimensions

- Metric signature: `(-,+,+,+)`.
- Spatial orientation: `epsilon_123=+1`.
- The photon propagation direction is `e`; the outward observed sky direction
  is `n=-e`.
- The local boost uses dimensionless `beta=v/c` and
  `gamma=(1-beta^2)^(-1/2)` on `beta^2<1`.
- `D`, the solid-angle Jacobian and all direction maps are dimensionless.
- `H_geom`, `sigma_ab`, `a_B^a`, `n_B^{ab}`, `Omega_triad^a`, `R` and `V^a`
  have dimension `L^-1` in the ray-length convention.
- Natural units are not assumed.

## Six-formula contract

In the outward-sky chart,

```text
D(n)=gamma(1+beta.n)
dOmega_tilde/dOmega=D^-2
T_tilde(n_tilde)=D T(n(n_tilde))
```

and in the photon-propagation chart the same Doppler factor is

```text
D(e)=gamma(1-beta.e),  n=-e.
```

The homogeneous photon coefficients remain

```text
R=-H_geom-sigma_ab e^a e^b
e_a V^a=0,
```

with the full direction flow carrying shear, the Bianchi commutator vector,
structure tensor and triad rotation. The local-observer boost is an output
pullback and is not a global matter tilt.

## Exact Wolfram checks

The connected stateless Wolfram 15.0.1 oracle passed:

- aberrated-direction unit norm;
- unboosted/boosted Doppler-chart equality;
- `dOmega_tilde/dOmega=D^-2`;
- invariance of the Planck argument under `nu_tilde=D nu`, `T_tilde=D T`;
- celestial-sphere tangency `e_a V^a=0`;
- FLRW limit `R=-H_geom`;
- six unique shared Formula IDs;
- twelve atomic-owner relation records;
- twenty-two unique exact source blobs;
- acyclic DAG with both 02C and 02D gating 02E.

All fifteen checks and seven hostile mutations passed. The canonical
InputForm SHA-256 is
`3ec0cd684b024a56d8c5232a96bb3af7307b8d435bb66d7d962abc18363e2aa8`.
This is not a native repository-file Wolfram replay.

## Hostile controls

The oracle rejects or detects:

1. Jacobian power `D^-1` instead of `D^-2`;
2. blackbody Doppler weight zero;
3. omission of the radial compensation in the direction flow;
4. a compound relation owner;
5. the stale four-formula union;
6. a 21-row source matrix;
7. removal of the 02D-to-02E prerequisite.

## Source-completeness result

Every exact file in REI PR #32 `src/rei_bianchi` is now bound to either:

- a named relation record; or
- a machine-readable exclusion disposition such as REI-owned numerical
  closure, runner-only surface, nonformula protocol, or typed absent ABI.

This is complete for the exact active 22-path tree. It is not a historical
all-branch duplicate search and does not claim line-by-line formal proof for
every excluded implementation.

## Ranked findings

- **P0:** none within the bounded relation classification.
- **P1:** 02E must remain held until repaired 02C and accepted/frozen 02D are
  both read back.
- **P1:** the six-formula export does not supply a BASS numerical background
  provider or REI anisotropic group-redshift closure.
- **P1:** finite-electron-tilt collision physics remains outside the exact
  cold, non-tilted electron-rest photon SSOT.
- **P2:** the HTT relation map is bounded to frozen WU-010/WU-011 authorities;
  current WU-011 advances do not change the exact Lorentz-pullback blob, but a
  consumer binding must still pin its chosen head.
- **P3:** literature references are cross-checks only and carry no project
  authority.

## Claim boundary

Allowed:

```text
COMPLETE_22_PATH_ACTIVE_REI_RELATION_OR_EXCLUSION_MATRIX
SINGLE_OWNER_RELATION_REGISTRY
SIX_RECORD_SHARED_FORMULA_UNION
CONNECTED_STATELESS_WOLFRAM_ORACLE_PASS
```

Withheld:

```text
02E_IMPLEMENTED
CROSS_REPOSITORY_SEMANTIC_EQUIVALENCE
GENERIC_BIANCHI_REI_TRANSPORT
FINITE_ELECTRON_TILT_COLLISION
BASS_BACKGROUND_PROVIDER
FIRST_CANONICAL_INTERVAL
PROVIDER_EXPORT
SCIENCE_OR_RF04_PROMOTION
```
