# PHYS-MATH audit — BASS-8B.2B.1

## Locked conventions

- Metric signature: `(-,+,+,+)`.
- Electron velocity: dimensionless normal-tetrad vector `beta_e`, with
  `|beta_e|<1`.
- Photon direction `e_i`: propagation direction in the normal tetrad.
- Rest quadrature `(e'_i,w'_i)` is fixed; normal nodes are its inverse-aberrated
  paired image.
- `n_e` is electron-rest proper density in `m^-3`.
- `sigma_T` is in `m^2`, `c` in `m s^-1`, and `H_n` in `s^-1`.
- `tau_Q` is dimensionless and future increasing.  Therefore derivatives with
  respect to `tau_Q` carry the same physical dimensions as their variables.

## Rate contract

Define

```text
gamma = (1-beta_e^2)^(-1/2)
q_i   = 1-beta_e.e_i
D_i   = gamma q_i = E_e/E_n
alpha = n_e sigma_T c/H_n
nu_i  = alpha D_i = (alpha gamma) q_i
```

The frozen 2B.0 collision carrier already contains the direction factor `q_i`.
The full Q-time generator is therefore

```text
C_Q = (alpha gamma) C_q,
```

not `alpha C_q` and not a second nodewise multiplication by `D_i`.

Dimensions:

```text
[n_e sigma_T c] = s^-1
[alpha]          = 1
[D_i]            = 1
[nu_i]           = 1
```

## Dual and projector contract

Let `C_q=M_q C_0`, where `M_q` multiplies each angular fiber by `q_i`.
For nonzero `q_i`, the right kernel is unchanged but the left kernel transforms:

```text
ker(C_q)   = ker(C_0)
left(C_q)  = M_q^{-T} left(C_0)
```

On the selected paired carrier the node weights are

```text
shape-left: w_i q_i^2/(4 pi)
full-left:  w_i q_i/(4 pi)
```

and

```text
(shape-left)/nu_i = (full-left)/(alpha gamma).
```

The residual global factor cancels from
`P=r a^T/(a^T r)`, while the direction-dependent factor does not.

## Jet contract

```text
gamma_dot = gamma^3 beta_e.dbeta_e
q_dot_i   = -(dbeta_e.e_i + beta_e.de_i)
D_dot_i   = gamma_dot q_i + gamma q_dot_i
alpha_dot/alpha = n_dot/n - H_dot/H
nu_dot_i  = alpha_dot D_i + alpha D_dot_i
```

Because the paired normal grid moves with `beta_e`, the `beta_e.de_i` term is
load-bearing.  The fixed-rest-node equivalent is

```text
D_i = 1/[gamma(1+beta_e.e'_i)].
```

Both forms and their derivatives agree exactly in the SymPy and Wolfram
witnesses.

## Limits and covariance

- Zero tilt: `e_i=e'_i`, `D_i=q_i=gamma=1`, `nu_i=alpha`.
- Type-II aligned tilt is a restriction of the generic-vector formula, not a
  transplanted convention.
- Simultaneous SO(3) rotation of rest nodes, `beta_e`, `dbeta_e`, and the tensor
  carrier leaves rates, rate jets, the generator, and the left dual covariant.
- Exact vacuum is `CollisionOff`; rate and generator vanish, electron velocity
  is quotiented, and no nontrivial collision projector is identifiable.

## Audit verdict

```text
No P0 formula/sign/unit failure found after the 2B.0 rate/dual correction.
```

Remaining limitations:

- Exact E2-owner host parity is prepared but was not executable in this sandbox.
- The supplied `H_n,H_dot_n` seam is provenance-typed but is not yet bound to a
  canonical VI0 background owner.
- The complete moving screen-map/equilibrium/left/projector differential is the
  next 2B.2 node.
- Near-luminal conditioning beyond the tested `|beta_e|<=0.75` is unclaimed.
