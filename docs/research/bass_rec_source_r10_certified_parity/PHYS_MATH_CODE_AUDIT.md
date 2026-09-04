# PHYS–MATH–CODE Audit — R10 Certified Scalar Projection Parity

## Equation-to-code map

| Contract | Code surface |
|---|---|
| canonical coefficient order | `canonical_real_harmonic_modes` |
| explicit constant-field coefficient | `unit_field_coefficients` |
| Condon–Shortley associated Legendre recurrence | `_associated_legendre`, `_real_harmonic` |
| sufficient GL x uniform-phi rule | `SphereQuadrature.create`, `build_gauss_legendre_uniform_phi_quadrature` |
| synthesis and projection | `synthesize_real_spherical_harmonics`, `project_real_spherical_harmonics` |
| same-source route comparison | `compare_constant_pair_grid_and_pstf` |
| deterministic provenance | `SourceParityContract`, `SourceParityReport` |

## Bounded production diff

The exact production commit adds one file:

```text
A  bianchi/source_parity.py
```

`source_authority.py`, `source_adapters.py`, backend dispatch, native core, dependency locks, package metadata, and solver loops remain unchanged.

## Input and identity guards

The implementation rejects:

- non-integer or negative ranks;
- coefficient-count mismatch with `(L+1)^2`;
- underresolved latitude or azimuth counts;
- malformed state, representation, or projection identities;
- identical grid/PSTF representation identities;
- supplied projection identity inconsistent with the generated quadrature;
- negative synthesized occupation samples on the full-grid source route;
- nonfinite inputs or outputs;
- parity residuals above the declared tolerance when `require_pass=true`.

The projection hash includes actual node and weight bytes, the real-basis convention, mode order, measure, work rank, and unit-field coefficients. The report hash binds both R8 output receipts, projected values, residuals, tolerance contract, time basis, and divisor.

## Required local evidence

1. all R5/R6/R7/R9 methods: 49/49;
2. rank sweep `L=0,1,2,3,4,6,8`;
3. two-process report identity;
4. source-parity residual and Gram defect at or below `2e-13`;
5. Gram infinity-condition estimate at or below 2;
6. normalization, underresolution, source-off, and projection-identity mutations;
7. fresh SymPy/mpmath attempt and bounded optional CAS probes;
8. clean detached source worktree.

## P1 risks before replay

- a recurrence or phase error could remain self-consistent in synthesis and projection while disagreeing with an external convention;
- the R9 tests validate one real-harmonic convention, not the production PSTF registry;
- report constructors remain public frozen dataclasses rather than factory-only authority objects;
- performance is deliberately unoptimized and scales poorly at high rank;
- no trusted-native parent/candidate differential has yet been executed for R10.

## Deferred

- anisotropic source multiplication and Gaunt/Wigner products;
- spin-weighted and polarized projection;
- actual BASS state-container and solver-loop wiring;
- frequency interpolation and nonlocal atomic kernels;
- integrated-state closure;
- optimized SHT libraries or GPU backends.

## Pre-execution verdict

```text
R10_MINIMAL_SOURCE_IMPLEMENTED
SOURCE_LEVEL_CONTRACT_REVIEWED
RUNTIME_GREEN_NOT_YET_CLAIMED
R10B_TRUSTED_NATIVE_DIFFERENTIAL_REQUIRED_AFTER_LOCAL_PASS
```
