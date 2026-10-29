# CE1-Q · 보존된 6-cell 무충돌 복사의 관측자 각도-에너지 하늘

**원본 조건:** signature (-,+,+,+), diagonal expanding Bianchi I, Λ=0, massless collisionless unpolarized radiation, six positive physical cells and eight independent coordinate reflections. `u=t/Tstar`; `ell_i=ln a_i`. The frozen energy units remain `E=(8πG Tstar²/c²) ρ_energy`, with matching dimensionless pressure. This node introduces neither a temperature spectrum nor local observer boost, global fluid tilt, collision or polarization.

**선행 저장소:** physical-history PR #258, HEAD `0656e98989750de4ea19c510ff2052654aaa3eda`; independent BASS Rust E/P/J PR #257, HEAD `baa29ff5b5d0384f62e2627ebc8b37d34d7aa26b`. Source mass/geometry module at PR #253: `einstein_tabulated_source.py` Git blob `fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf`. Original exact input binary SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

## 1. Canonical momentum and observer-tetrad map (derived)

`ds²=-c²dt²+Σ_i a_i²(t)(dx^i)²`, with the normal congruence `u^a`. Since `∂_i` are Killing, covariant spatial momenta `q_i=p_i` are conserved along each collisionless null characteristic. With `a_i(0)=1`, let `q_i=q n_{0i}`. The measured orthonormal spatial momentum is `p_hat_i=q_i/a_i` and its energy is `ε=c q r`, where

```
M = diag(exp(-ell_i)), det M = exp(-Σ ell_i),
r(n0) = |M n0|, n_photon = M n0 / r, s_observed_sky = -n_photon.
```

**Sign convention:** `s` is incoming sky location, the *opposite* of photon propagation `n`. All energy densities in this report are normal-frame scalar or angular fields and the eight reflected source is even, so odd-l coefficients vanish, but the convention matters in non-even extensions.

## 2. Projective sphere Jacobian (derived + Wolfram symbolic zero)

For any positive invertible 3×3 `M`, the radial map `F(n0)=M n0/|M n0|` has oriented surface-area Jacobian

```
dOmega_obs/dOmega_0 = det(M) / r(n0)^3.
```

Proof: `dF=(I-FF^T)M dn0/r`; take the oriented triple product `F·(dF_theta×dF_phi)` and use the determinant identity. Wolfram independently evaluated the diagonal Bianchi-I cross-product expression minus `det(M)/r³` and returned **0**, within real positive-scale assumptions. This map is angular measure transport, **not** spatial beam area/luminosity distance.

## 3. Energy-integrated brightness and exact moment bridge (derived)

The original six cell energies `E_ij` represent integrated **angular** radiation energies over eight coordinate-sign octants. With `mu=|n0_z| ∈ [0,1]`, `t=(2/pi)atan2(|n0_y|,|n0_x|) ∈ [0,1]`, their piecewise-constant initial angular density is

```
U0(n0 in cell ij) = E_ij / (4*pi*(mu_{i+1}-mu_i)*(t_{j+1}-t_j)).
```

A comoving physical volume grows as `V=exp(Σ ell_i)`; each conserved canonical ray contributes energy `r` relative to its initial value. Thus the pushforward energy measure is `dE_u = det(M) * r * U0(n0) * dOmega_0`, from which

```
U_u(s(n0)) = U0(n0) * r(n0)^4,
E_u=∫ U_u(s)dOmega_s = det(M)∫r U0 dOmega_0,
P_ij=∫ U_u(s) s_i s_j dOmega_s.
```

**Crucial scope:** For the original six *continuous* cells, `U_u(s)` is a positive (piecewise-smooth, discontinuous-boundary) function. For any finite set of stored quadrature rays, the sky remains an *atomic measure*. Its pointwise brightness function is **not defined** without explicitly adding smoothing. Both have finite spherical harmonic moments.

## 4. Direct sky harmonics and quadrupole pressure identities (derived)

Define standard orthonormal Condon–Shortley complex `Y_lm`, and `a_lm^U(u)=∫ U_u(s)Y_lm^*(s)dOmega_s`. With `s(n0)=-M n0/r`,

```
a_lm^U = det(M) ∫ U0(n0) r(n0) Y_lm^*(s(n0)) dOmega_0.
```

For each stored positive-octant ray `(w_a,n_a)`, calculate the average of `Y*` over all 8 reflected signs with physical weight `det(M)*w_a*r_a/8`. Do not multiply `w_a` by 8: it already includes the eight octants. When `l<=4`, the normal-frame brightness monopole and diagonal stress imply

```
a_00 = E / sqrt(4*pi)
a_20 = sqrt(5/(16*pi)) * (3 P_3 - E)
a_22 = sqrt(15/(32*pi)) * (P_1 - P_2)
a_2,-2 = a_22*;
```

and reflection-even sky eliminates every odd `l` and odd `m`. Complex field reality obeys `a_l,-m = (-1)^m conj(a_lm)`. It also fixes the square-integrated *model energy* multipole statistic `C_l^U=(Σ_m |a_lm^U|²)/(2l+1)`. This is **not** thermodynamic temperature `C_l`, not brightness/polarization Q/U, and has no likelihood interpretation.

The existing BASS Rust `_rustcore/src/kinetic/comoving.rs` supplies `Frame::apply`, `Frame::det`, `phys_dirs` and the `l=2` real tesseral basis. The new Rust CLI merely adds `l=3,4` complex-harmonic projection, without modifying its original module. BASS `Frame::step` uses e-fold time and is **not** invoked with proper-time `u` as its numerical clock: here `M(u)` is constructed from already evolved `ell_i(u)`.

## 5. Exact checks and limits

- `M=I`: `U_u(s)=U0(-s)`; original anisotropic 6-cell initial source can have nonzero `a20`, `a22` even before geometric evolution.
- Isotropic uniform scaling `M=λI`: `U_u=λ^4 U0`, and every `a_lm^U` scales as `λ^4`.
- Eight Cartesian reflections ensure off-diagonal `P_ij=0` and all odd-l/odd-m coefficients zero in exact arithmetic, without applying a post hoc zeroing filter.
- `E=Σ P_i`, `a_00 sqrt(4π)=E`, plus the `a20`/`a22` formulas must agree with independently saved CE1-P `E/P` for each time.
- The source is nonnegative, geometric scales positive, `0<=u<=0.08`, and all angular ray/mass byte identities are preserved. The exact stored ref8 `(n,mass)` SHA pair is `9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba` and `c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211`.
- Original PR #255 MPFR192 bounds concern the **separate four-panel RK4/Hermite geometry**, not these CE1-P DOP853 histories, nor any new sky harmonic. This code has no new formal interval certificate.

## 6. Theoretical provenance and scientific context

The conserved-momentum tetrad map is compatible with Fleury–Pitrou–Uzan (2015), *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511, DOI:10.1103/PhysRevD.91.043511; massless Bianchi-I Einstein–Vlasov context follows Lee–Nungesser–Tod (2020), *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen. Relativ. Gravit. 52,48, DOI:10.1007/s10714-020-02699-7. These references support background kinematics and physical domain, **not** acceptance of the new BASS implementation or an observational CMB inference. The Jacobian, angular pushforward, and quadrupole bridge above are derived for the present contract and their numerical forms tested separately.

**DAG:** existing top-level BASS 9/15, 21 edges. New scoped research output is separate and does not by itself close CE-1. Independent distinct-author R6/C9 NOT_RUN.
