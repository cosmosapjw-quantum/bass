# PHYS–MATH audit — R9 finite-rank nonaxisymmetric parity RED

## Conventions and dimensions

- Metric signature remains `(-,+,+,+)`.
- The photon occupation is dimensionless.
- `eta`, `kappa`, and `chi_affine=kappa-eta` have dimensions `T^-1`.
- The speed of light remains explicit.
- The angular basis is orthonormal with respect to `dOmega`.

The photon/boson source is

```text
C_t[f] = eta*(1+f)-kappa*f
       = eta-(kappa-eta)*f.
```

For any linear angular projector `Pi`,

```text
Pi C_t[f] = eta Pi[1]-(kappa-eta) Pi[f].
```

The real harmonic convention is fixed by

```text
Z_l0      = Y_l0
Z_lm^cos  = sqrt(2) Re Y_lm
Z_lm^sin  = sqrt(2) Im Y_lm, m>0,
```

where `Y_lm` includes the Condon–Shortley phase. Hence the constant unit field has coefficient `sqrt(4*pi)` in the monopole slot.

## Quadrature sufficiency for the bounded source

For a field and output both band-limited to `L_work`, azimuthal products have Fourier content at most `2 L_work`. A uniform rule with `N_phi >= 2 L_work+1` therefore prevents a nonzero mode from aliasing into the zero Fourier mode.

After exact azimuth selection, associated-Legendre products are polynomials in `mu=cos(theta)` of degree at most `2 L_work`. Gauss–Legendre with `N_mu=L_work+1` is exact through degree `2 L_work+1`.

This sufficiency applies to the current angularly constant source. A source with rank `L_source>0` requires the later product-domain condition

```text
L_work >= L_out + L_source
```

and an explicit Gaunt/Wigner implementation. R9 does not add that physics.

## Time and length bases

If `d tau = H dt` on the expanding chart,

```text
C_tau = C_t/H,  H>0.
```

For ray length `ds=c dt`,

```text
C_s = C_t/c.
```

The same divisor must be applied exactly once in both routes.

## Limits

- `eta=kappa=0` gives exact source-off parity.
- `eta>kappa` gives a valid negative-`chi_affine` stimulated-growth branch.
- `H=0` remains outside the current Q-time chart.
- The test is scalar, finite-rank, band-limited, and frequency-bin local.
- It is not a transport-time parity theorem and not a physical REC-source validation.

## Verdict

The bounded parity contract is mathematically consistent. Its implementation is intentionally absent at R9, so no numerical parity claim is admitted yet.
