# PHYS–MATH Audit — R8 Constant-Pair Dual Adapter

## Conventions

- Metric/sign conventions are inherited unchanged from the qualified R6 source authority.
- Occupation `f` is dimensionless.
- `eta_s_inv`, `kappa_s_inv` and `chi_affine_s_inv=kappa_s_inv-eta_s_inv` have units `T^-1`.
- `eta>=0` and `kappa>=0`; the derived affine coefficient may be signed.
- The adapter retains `c` explicitly and does not assume natural units.

## Source identity

For photons with bosonic statistics,

```text
C_t[f] = eta*(1+f)-kappa*f
       = eta-(kappa-eta)*f.
```

The full-grid action evaluates this pointwise. For a linear coefficient projector `Pi`,

```text
Pi C_t[f] = eta Pi[1]-(kappa-eta) Pi[f].
```

The coefficient route therefore requires the caller's explicit coefficient vector for the constant unit field. It does not assume that the monopole coefficient equals one in every normalization.

## Time and length conversion

If `d tau = H dt`, then

```text
C_tau = C_t/H,
```

with `H>0` on the current expanding-Q-time chart. If the transport operator is written per ray length,

```text
C_L = C_t/c.
```

The adapter admits exactly one divisor for each nonphysical-time basis and rejects surplus or missing conversion inputs.

## Rank and information domain

The first source is angularly constant, so `L_source=0` and

```text
L_work >= L_out.
```

No claim is made for an anisotropic finite-band source. Radial-integrated angular grids and finite integrated-J hierarchies remain outside the pointwise-spectral adapter domain.

## Exact fixture

```text
f(mu)=0.9 P0+0.2 P1-0.1 P2+0.05 P3
eta=3, kappa=2, chi_affine=-1
C[f]=3+f
```

Hence the coefficient source in this normalization is

```text
(3.9, 0.2, -0.1, 0.05).
```

A four-node Gauss–Legendre projection is exact through this rank because the projected integrands have polynomial degree at most six.

## Limits and counterexamples

- Source off: `eta=kappa=0` gives zero.
- Stimulated growth: `eta>kappa` gives `chi_affine<0` without invalid primary rates.
- Vacuum-only testing is insufficient: dropping the `eta*f` stimulated term is invisible at `f=0`.
- `H=0` is outside the Q-time adapter chart.
- A generic source-integrated state cannot be reconstructed from one pointwise constant pair.

## Verdict

The bounded equations, signs, dimensions and exact low-order projection fixture are internally consistent. This does not establish a nonaxisymmetric all-rank adapter, a frequency-dependent REC source, transport evolution or numerical grid/PSTF parity.
