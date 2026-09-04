# BASS–REC Source R7 — Full-grid / spectral-PSTF adapter TDD RED

**Date:** 2026-09-04  
**Stage:** `BASS_REC_SOURCE_R7_FULL_GRID_AND_SPECTRAL_PSTF_ADAPTER_TDD_RED`  
**Disposition:** `EXPECTED_RED / PRODUCTION_UNCHANGED`  
**Authority effect:** `NONE`

## Opened prerequisites

Both required gates have passed:

```text
PASS_BASS_REC_SOURCE_R6C_CLEAN_BACKEND_NONREGRESSION
AND
PASS_R5D_TRUSTED_RF00_PAYLOAD_PROVENANCE_AND_BACKEND_GATE
```

The exact BASS parent is:

```text
commit  6ffbcceb660896f29d569533f0349c8ebaafbbe1
tree    ee628ac799cd183591b3d1fdb7aa1e8f47008404
source  92d67dc79cf645947beb93ac01a9505ee277dabd
blob    869677390004f68aef9f547e6556f5f1c15bd012
```

The REC trusted-authority closeout is:

```text
repository  cosmosapjw-quantum/rec_bianchi
PR          #55
commit      29c01cec6f0e1fe02a738df0fe317ea2772d4c88
tree        7f74678b357ac3ebfc4cfa72e690dd6be9854de2
```

## Narrow objective

Freeze the first receiving adapter contract for one already-admitted,
frequency-local, constant positive photon/boson source pair:

```text
C[f] = eta*(1+f) - kappa*f = eta - (kappa-eta)*f.
```

The same immutable source payload must act on:

1. a direct full-spectral/angular-grid state;
2. spectral PSTF/harmonic coefficients.

For an explicitly supplied unit-field coefficient vector, the constant-pair
coefficient action is

```text
C_alpha = eta * 1_alpha - chi_affine * f_alpha.
```

An axisymmetric Legendre witness checks that grid application followed by
projection agrees with native coefficient-space action on the declared finite
polynomial domain.

## Why the unit-field coefficients are explicit

The coefficient representing the constant function depends on basis
normalization. R7 therefore does not assume that the monopole coefficient is
numerically one in every PSTF/Wigner convention. The caller must supply the
unit-field coefficients and bind them through a projection-contract SHA-256.

## Time and length bases

The REC source rates are physical-time rates with dimension `T^-1`.

```text
d_tau = H_s_inv * dt
eta_per_tau = eta_s_inv / H_s_inv
kappa_per_tau = kappa_s_inv / H_s_inv
```

For a ray-length operator written with `(1/c) partial_t`,

```text
eta_per_length = eta_s_inv / c
kappa_per_length = kappa_s_inv / c.
```

The conversion is selected by a typed time-basis enum and applied exactly
once. Ambiguous combinations fail closed.

## Intentional RED

The test imports the future module:

```text
bianchi.source_adapters
```

which is absent at the pinned parent. The intended local fingerprint is:

```text
12 tests run
10 assertion failures
0 errors
2 passing survivor controls
```

The passing controls preserve the R6 source authority and independently verify
exact low-order Legendre reconstruction/projection. Every adapter test fails
because the future module is absent.

## Exclusions

This stage does not add:

- a physical recombination source table or history;
- anisotropic or frequency-nonlocal source coefficients;
- two-photon or Raman kernels;
- polarized REC sources;
- finite-electron-tilt collision;
- integrated `G(e)` or `J^(i)_{A_l}` closure;
- solver-loop wiring;
- numerical grid/PSTF convergence or parity;
- a 26-direction physical face;
- provider or statistics output.

## Next node

Only after the exact expected RED is observed may the minimal implementation
node open:

```text
BASS_REC_SOURCE_R8_CONSTANT_PAIR_DUAL_ADAPTER_GREEN
```

R8 must remain a pure receiving adapter and must not duplicate REC atomic
microphysics or BASS's existing PSTF/Gaunt compiler.
