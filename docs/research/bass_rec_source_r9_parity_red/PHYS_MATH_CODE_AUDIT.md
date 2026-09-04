# PHYS–MATH–CODE audit — R9 RED

## Equation-to-code target

| Contract | Future code surface |
|---|---|
| canonical real-harmonic modes | `canonical_real_harmonic_modes` |
| explicit unit field | `unit_field_coefficients` |
| sufficient tensor-product rule | `SphereQuadrature`, `build_gauss_legendre_uniform_phi_quadrature` |
| synthesis / projection | `synthesize_real_spherical_harmonics`, `project_real_spherical_harmonics` |
| same-source route comparison | `compare_constant_pair_grid_and_pstf` |
| typed result and provenance | `SourceParityContract`, `SourceParityReport` |

## Current code reality

- `bianchi/source_authority.py` remains the qualified R6 source authority.
- `bianchi/source_adapters.py` remains the qualified R8 constant-pair adapter.
- `bianchi/source_parity.py` is absent.
- The R9 source change is exactly one test file.
- Backend, native core, solver loops, requirements and package metadata are unchanged.

## Expected RED integrity

The fourteen future-behavior tests all fail at the missing parity module. Two controls pass:

1. exact rational affine-projector linearity;
2. the existing R8 grid and coefficient adapters.

A collection error, syntax error, missing dependency, changed survivor result, or unexpected failure count is not an admissible RED.

## P1 risks deliberately exposed

1. harmonic normalization or mode-order drift;
2. silent latitude or azimuth aliasing;
3. different source or state-parent identities on the two routes;
4. applying Q-time or ray-length conversion twice or not at all;
5. treating a low-order axisymmetric fixture as generic nonaxisymmetric parity;
6. failing to detect sign or unit-field normalization mutations.

## Deferred

- angularly varying source multiplication and Gaunt kernels;
- polarization and spin-weighted transforms;
- frequency interpolation and nonlocal atomic kernels;
- actual BASS state/solver wiring;
- integrated-state closure;
- performance optimization.

## Verdict

R9 is a coherent test-first boundary. R10 must add only the minimal parity module required by this contract, then undergo trusted-native and residual-plot validation before any solver wiring.
