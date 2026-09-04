# PHYS–MATH Audit — R10A Projection Authority Hardening

## 1. Fixed conventions

- scalar real harmonics are orthonormal on `dOmega`;
- complex parent harmonics use the Condon–Shortley phase;
- mode order is `(ell,0,m0),(ell,1,cos),(ell,1,sin),...`;
- grid flattening must be declared as `mu_major_phi_minor`;
- the source law remains

```text
C_t[f] = eta*(1+f)-kappa*f = eta-chi*f,
chi = kappa-eta.
```

`eta`, `kappa`, and `chi` have dimensions `T^-1`; `f` and the harmonic basis are dimensionless. Q-time and ray-length source coefficients are obtained by exactly one division by `H` and `c`, respectively.

## 2. Finite-rank projection theorem

Let `Z_alpha` be the locked real orthonormal basis through output rank `L_out`, and let

```text
B_(ij,alpha) = Z_alpha(mu_i,phi_j),
W_(ij,ij) = w_i * 2*pi/N_phi.
```

For a scalar field band-limited at `L_p`, projection through `L_out` is exact when the tensor-product rule integrates `Z_alpha f` for every retained mode. A sufficient rule is

```text
2*N_mu - 1 >= L_p + L_out,
N_phi > L_p + L_out.
```

Equivalently,

```text
N_mu  >= ceil((L_p+L_out+1)/2),
N_phi >= L_p+L_out+1.
```

For the current constant source, `L_p=L_out=L_work=L`, so this reduces to

```text
N_mu >= L+1,
N_phi >= 2*L+1.
```

The discrete projector is exact on the declared subspace when

```text
B^T W B = I.
```

This is a theorem about the realized operator `B,W`, not merely a coefficient count.

## 3. Source commutation

For coefficients `a=Pi_L f` and the unit-field vector `u=Pi_L 1`, linearity gives

```text
Pi_L C_t[f] = eta*u - chi*a.
```

The identity remains true in Q-time and ray length:

```text
Pi_L C_Q[f] = (eta*u-chi*a)/H,
Pi_L C_s[f] = (eta*u-chi*a)/c.
```

Therefore a comparison contract for one execution must bind the actual `u`, independent-variable basis, and divisor. Binding them only in a later report is insufficient if the contract itself is advertised as the comparison authority.

## 4. Semantic identity versus realized identity

One hash cannot safely play both roles.

The semantic specification should bind exact declarations:

```text
projection_spec = {
  schema,
  measure,
  normalization,
  Condon-Shortley phase,
  real-basis definition,
  mode order,
  sample layout,
  L_work,
  N_mu,
  N_phi,
  quadrature algorithm id,
  basis algorithm id
}.
```

Its identity is

```text
H_spec = SHA256(canonical(projection_spec)).
```

The realized binary64 operator should additionally bind

```text
mu_i, w_i, phi_j, omega_j, B_(ij,alpha)
```

through hexadecimal floating representations:

```text
H_B    = SHA256(canonical(B_hex)),
H_real = SHA256(canonical(H_spec,nodes_hex,weights_hex,H_B)).
```

`H_spec` is a semantic identity. `H_real` is a byte/realization identity. Cross-platform equality is required only where explicitly claimed.

## 5. Use-time integrity

Python `frozen=True` is not valid-by-construction authority. Low-level assignment, deserialization, or forged objects can bypass the generated guard. Every public synthesis/projection/comparison boundary must therefore recompute the declared identities and reject any mismatch.

Minimum numerical invariants are:

```text
all entries finite,
-1 < mu_i < 1 and strictly ordered,
w_i > 0,
phi_j in [0,2*pi) and in declared order,
omega_j > 0,
sum_i w_i ~= 2,
sum_j omega_j ~= 2*pi,
N_mu >= L_work+1,
N_phi >= 2*L_work+1,
recomputed H_spec/H_B/H_real equal stored identities.
```

## 6. Continuous positivity

Node positivity is not a theorem of global positivity. For

```text
f(n) = a_00 Y_00(n) + sum_(ell=1)^L sum_m a_(ell m) Y_(ell m)(n)
```

in the orthonormal `dOmega` basis, the addition theorem and Cauchy–Schwarz give the shellwise bound

```text
|sum_m a_(ell m) Y_(ell m)(n)|
  <= sqrt((2*ell+1)/(4*pi)) * ||a_ell||_2.
```

Hence the following is a sufficient, conservative, analytic positivity certificate:

```text
a_00 > sum_(ell=1)^L sqrt(2*ell+1) * ||a_ell||_2.
```

The simpler global bound

```text
a_00 > sqrt((L+1)^2-1) * ||a_>0||_2
```

is also sufficient. If neither certificate nor a stronger interval/SOS proof is present, the report must state

```text
continuous_positivity_certified = false.
```

## 7. Acceptance metric

The componentwise parity gate is

```text
|r_alpha| <= atol + rtol*max(|g_alpha|,|p_alpha|).
```

The dimensionless quantity that directly measures proximity to failure is

```text
rho_alpha = |r_alpha|/(atol+rtol*max(|g_alpha|,|p_alpha|)),
rho_max = max_alpha rho_alpha.
```

Admission is `rho_max <= 1`. A plot containing only a flat absolute-tolerance line is not the actual acceptance diagnostic.

## 8. High-rank recurrence route

The current implementation separately forms an unnormalized associated Legendre function and a small factorial normalization. That separation is not a safe arbitrary-rank method. Define instead

```text
Pbar_(ell m)(x)
 = sqrt((2*ell+1)/(4*pi) * (ell-m)!/(ell+m)!) * P_ell^m(x).
```

The fully normalized Condon–Shortley recurrence is

```text
Pbar_(m m)
 = -sqrt((2*m+1)/(2*m))*sqrt(1-x^2)*Pbar_(m-1,m-1),

Pbar_(m+1,m)
 = sqrt(2*m+3)*x*Pbar_(m m),

Pbar_(ell m)
 = A_(ell m)*x*Pbar_(ell-1,m)
   - B_(ell m)*Pbar_(ell-2,m),

A_(ell m) = sqrt((4*ell^2-1)/(ell^2-m^2)),

B_(ell m) = sqrt(
  (2*ell+1)/(2*ell-3)
  * (((ell-1)^2-m^2)/(ell^2-m^2))
).
```

This removes the largest analytic cancellation but does not by itself certify arbitrary degree. A high-L implementation must still use dynamic scaling, Clenshaw/Fourier methods, or a qualified SHT library and must be cross-validated independently.

## 9. Verdict

```text
R10 finite-rank behavior survives.
R10 projection authority is not yet closed.
R10A expected RED is the correct next serial node.
No trusted-native, production-PSTF, transport, or physical-REC promotion is allowed before R10A GREEN.
```
