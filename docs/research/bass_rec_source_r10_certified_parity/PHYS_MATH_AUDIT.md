# PHYS–MATH Audit — R10 Certified Scalar Projection Parity

## Scope

R10 introduces no new collision or transport equation. It implements a finite-dimensional scalar angular representation bridge for the already-qualified constant photon/boson source.

## Conventions

- spacetime signature remains `(-,+,+,+)`;
- spatial orientation remains `epsilon_123=+1`;
- occupation `f` is dimensionless;
- `eta`, `kappa`, and `chi_affine=kappa-eta` have dimensions `T^-1`;
- `c` is explicit;
- the real scalar harmonics are orthonormal with respect to `dOmega` and inherit the Condon–Shortley phase.

The source law is

```text
C_t[f] = eta*(1+f)-kappa*f
       = eta-(kappa-eta)*f.
```

For a linear finite-rank projector `Pi_L`,

```text
Pi_L C_t[f] = eta Pi_L[1]-(kappa-eta) Pi_L[f].
```

## Normalization

With `Y_00=1/sqrt(4*pi)` on `dOmega`,

```text
1 = sqrt(4*pi) Y_00.
```

The constant source therefore enters through the explicit unit-field coefficient vector; it is not hard-coded as a numerical coefficient one. This differs from a mean-normalized `dOmega/(4*pi)` convention but is not inconsistent with it.

## Quadrature sufficiency

For the current angularly constant source, both input and requested output have rank at most `L_work`. Harmonic products contain azimuthal order at most `2 L_work` and, after azimuthal selection, polynomial degree in `mu=cos(theta)` at most `2 L_work`. The sufficient tensor-product rule is therefore

```text
N_phi >= 2 L_work+1,
N_mu  >= L_work+1.
```

The implementation chooses equality and rejects one-node underresolution in either direction.

## Independent-variable bases

```text
d tau = H dt, H>0     => C_tau = C_t/H,
ds = c dt             => C_s   = C_t/c.
```

The same divisor must be applied exactly once in both representation routes.

## Known limits

- `eta=kappa=0` gives exact source-off parity;
- `eta>kappa` gives a valid stimulated-growth branch with negative `chi_affine`;
- `H=0` remains outside the expanding Q-time chart;
- the current theorem is scalar, finite-rank, band-limited, frequency-bin local, and angularly constant in its source coefficients.

## Scope firewall

The Formula SSOT supplies analytic all-rank PSTF/Wigner authority for the homogeneous Liouville-plus-cold-Thomson core but explicitly excludes recombination microphysics, numerical truncation, solver construction, and time evolution. R10 therefore cannot promote its finite-grid parity result into an all-rank transport or physical-REC claim.

## Pre-execution verdict

```text
PHYS_MATH_CONTRACT_CONSISTENT
FINITE_RANK_SCALAR_CONSTANT_SOURCE_ONLY
LOCAL_49_TEST_AND_RESIDUAL_REPLAY_REQUIRED
NO_TRANSPORT_OR_PHYSICAL_REC_PROMOTION
```
