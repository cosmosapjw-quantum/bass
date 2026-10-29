# BASS CE1-V | 동일한 연속 운동량 source의 두 시점 angular-energy cross-power

**Date:** 2026-10-30 KST. **Status:** DERIVED + NUMERICALLY CHECKED for the original source only. **Top-level original DAG:** **9/15**, 21 edges, CE1 PARTIAL, no merge / production claim.

## 1. 물리·자료 계약

Metric signature (-,+,+,+), `ds²=-c² dt² + Σ_i a_i(t)² (dx^i)²`, `u=t/Tstar ∈ [0,0.08]`, `h_i=d ln a_i/du`; diagonal expanding Bianchi I, Λ=0, massless collisionless positive reflection-even radiation, normal comoving tetrad, initial `a_i=1`, initial shear `(0.2,-0.13,-0.07)`. Preserve the **original exact binary64 six-cell** initial angular distribution and all eight coordinate reflections; initial energy `E0=0.9`. Frozen input SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

Primary input is CE1-U PR #264 HEAD `15bb9fd015570c1562a4a7b9102f25a8481796f5`, coupled **actual GL6 and GL8 Einstein–Vlasov 41-step numerical trajectories**: exactly extracted from CE1-U verified corrected ZIP SHA256 `d3f0e8196dc0a4a466cfc1932ed0d9385bcc79175773a5f9ecaee69871527fa4`; their immutable raw bytes have distinct SHA256 values in `inputs/SOURCE_CONTRACT.json`. No newly fitted source or fluid closure. The separate sibling PR #265 HEAD `bcbb2ba451b9026608525cce27e26cf1a1288161` (MPFR four-panel, conditional) is **context**, not imported or merged. Its time-bound hypotheses and binary data must be validated independently before transfer to two-time kernels.

## 2. Transported observer sky and angular harmonics

The translational Killing vectors conserve covariant momenta `q_i`. Let `M=diag(exp(-ell_i))`, `r(n,u)=|Mn|`, `s=-Mn/r` be the *incoming* observer sky direction and `V=∏a_i`. If `dµ0=U0(n)dΩ0` is initial bolometric energy angular measure, its time-u observer-energy pushforward is `dµu(s)=det(M)r dµ0(n)`. At points where continuum density exists, `Uu(s)=r^4 U0(n(s))` and `dΩ_s=det(M)r^(-3)dΩ0`. A GL source is the discrete measure version, not a smooth sky density.

Define orthonormal Condon–Shortley spherical harmonics `∫|Y_lm|²dΩ=1`, and its moment `a^U_lm(u)=∫Y_lm*(s)dµu(s)`. `a_00=E/√(4π)`.

The fractional bolometric contrast is `δ_u(s)=4π U_u(s)/E(u)-1`. For `l≥1`, `a^δ_lm(u)=(4π/E(u))a^U_lm(u)`. **This is not a thermodynamic CMB temperature field**, and uses no frequency spectrum or Q/U polarization.

## 3. New deterministic unequal-epoch kernel (no ensemble assumption)

For fixed identification of the normal comoving tetrad spatial axes across epochs, define

`K^U_l(u,v)=(1/(2l+1)) Σ_{m=-l}^l a^U_lm(u) conj(a^U_lm(v))`,

`K^δ_l(u,v)=(4π)^2 K^U_l(u,v)/(E(u)E(v))`.

Then `K_l(v,u)=conj(K_l(u,v))`, `K_l(u,u)=C_l(u)`, and for any finite complex `{z_j}`:

`Σ_ij conj(z_i) K_l(u_i,u_j) z_j=(1/(2l+1)) Σ_m |Σ_i z_i conj(a_lm(u_i))|² >=0`.

Hence each two-time matrix is Hermitian positive semidefinite and, whenever diagonal entries are positive, `|r_l(u,v)|≤1` for `r_l=K_l(u,v)/sqrt(C_l(u)C_l(v))`. This is a **deterministic Gram kernel**, NOT a stochastic covariance, cosmic variance, or a direct observation of two different lightcones.

With all three independent reflections, only *even* `l,m` survive. The real independent amplitudes used for the native BASS CE1-U source are exactly `a20,a22` for l=2 and `a40,a42,a44` for l=4. The correct ±m multiplicity is **2**, not 4:

`K^U_2(u,v)=[a20(u)a20(v)+2a22(u)a22(v)]/5`,

`K^U_4(u,v)=[a40(u)a40(v)+2a42(u)a42(v)+2a44(u)a44(v)]/9`.

For these finite-dimensional projections the sampled kernel ranks cannot exceed 2 and 3, respectively. **That kinematic rank is not a full Vlasov dynamical moment closure.**

Define the squared pattern separation

`D_l²(u,v)=C_l^δ(u)+C_l^δ(v)-2 Re K_l^δ(u,v)≥0`.

It measures the sum of relative amplitude and pattern changes, while `r_l` is the cosine between coefficient vectors with amplitude factored out.

## 4. Proper-time derivatives and the angle-separated rotational average

Under the frozen source, `b=Σ_i h_i s_i²`, `s_i'=(b-h_i)s_i`, `W'=-(θ+b)W`. Thus `a_lm'(u)` is supplied by CE1-R's direct BASS Rust Liouville formula (already verified) and propagated into CE1-U coupled data. At fixed v,

`∂_u K^U_l(u,v)=Σ_m a_lm'(u) conj(a_lm(v))/(2l+1)`;

`∂_u K^δ_l=(4π)²/(E(u)E(v)) [∂_u K^U_l - E'(u)K^U_l/E(u)]`.

At v=u, `[∂_u+∂_v]K_l^U(u,v)|_(v=u)=dC_l^U(u)/du`; for real reflection-even modes it equals `2∂_u K_l^U(u,u)`. The same holds for δ fields. This is testable without finite differences; finite differences of 41 physical samples are an additional nonrigorous diagnostic.

For the two *full* deterministic contrast skies on the same coordinate unit sphere, averaging their real-space correlation over common SO(3) frame rotations and using the spherical-harmonic addition theorem gives

`bar ξ_{uv}(γ)= Σ_{l=1}^∞ (2l+1)/(4π) K^δ_l(u,v) P_l(cosγ)`.

Only its **l=2,4 truncation** is generated in this unit: `bar ξ^(≤4)=[5 K2^δ P2+9 K4^δ P4]/(4π)`. It is NOT the full anisotropic orientation-dependent two-point function or a two-time CMB likelihood. Reflection gives `ξ(γ)=ξ(π−γ)` for this even-l truncation.

## 5. Numerical implementation and scope

`source/build_crosstime.py` loads *byte-verified frozen CE1-U coupled source CSVs* and constructs two 41×41 cross-kernels (GL6 216 source rays; GL8 384 source rays), raw 1681-row CSV each; l=2/4 cross-power and time derivatives; normalized power; complex-parity Gram tests; rank and Cauchy checks; and 181-angle rotation-averaged real-space arrays saved as compressed NPZ. `tests/test_two_time_physics.py` independently integrates the actual original six-cell angular distribution through `scipy.special.sph_harm_y` for u=0,0.04,0.08 and independently checks cross-time endpoint overlaps, kinetic E/P quadrupole formulas, time differentiation, angular parity, PSD and original byte identities.

Caveats: GL6-vs-GL8 discrepancy is **empirical quadrature/data comparison**, not a new certified continuum cross-time bound. Sibling PR #265's conditional h error cannot be promoted to a certified `K_l` error without bounding the source-to-observable functional derivative and the actual stored trajectory error. No new MPFR trajectory calculation, no new spectral assumption, no polarization. Original top DAG stays 9/15 (21 edges), CE1 PARTIAL, R6/C9 distinct-author NOT_RUN, native subagent NOT_EXPOSED, no merge/auto-next.

## 6. Literature connections (not endorsements of this model)

- Fleury, Pitrou, Uzan, *Light propagation in a homogeneous and anisotropic universe*, Phys. Rev. D 91, 043511 (2015), DOI 10.1103/PhysRevD.91.043511: Bianchi-I null-ray momentum, observer-frame redshift and direction conventions.
- Gebbie and Ellis, *GIC approach to Cosmic Background Radiation Anisotropies: Part I* (1998), arXiv:astro-ph/9804316: angular multipole representation and tensor/harmonic geometry.
- Campagne, Plaszczynski, Neveu, *The Galaxy Count Correlation Function in Redshift Space Revisited* (2017), DOI 10.3847/1538-4357/aa7cf8: a distinct application of the spherical-harmonic addition theorem to correlation functions. No claim of equivalent BASS physical system.

CE1-V's Gram-kernel definition, its proofs and model-specific numerical values are **our direct derivation / calculation**, not attributed to those papers.