# BASS CE1-S | Fractional bolometric sky anisotropy from frozen Liouville atlas

Date: 2026-10-30 KST. Scope: CE1-S new fractional angular-energy observable built on physically validated CE1-R Rust atlas; NOT a new matter closure.
Pinned inputs: PR #258 SHA `0656e98989750de4ea19c510ff2052654aaa3eda`, PR #259 SHA `e963b3cff4a6f91d4060e05080d1e6e2667e001b`, CE1-R PR #261 CI source SHA `950cf4ba2aca7130c6266298c870aed1a0b7db02`, subsequent pinned analysis parent SHA `c30f7e9a4987a0f1e57d003da56738bbafe49525`, original source binary64 table SHA-256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`.

## Assumptions and conventions

Metric `ds²=-c²dt²+Σ_i a_i²(t)(dx^i)²`, sign (-,+,+,+), a_i(0)=1, Λ=0. Positive reflection-even spatially homogeneous massless collisionless initial distribution; no new source, spectral occupation model, Thomson collision/polarization, tilted tetrad, or observational likelihood. Proper dimensionless clock `u=t/Tstar` with 41 epochs u=0,...,0.08, h_i=d(ln a_i)/du, θ=Σ h_i. Normal-comoving orthonormal observer. Initial conserved covariant momentum q_i and original six-cell initial angular-energy measure `U0(qhat)dΩq`. Incoming sky direction s=-M qhat/r, M=diag(e^{-ell_i}), r=|M qhat|, detM=e^{-Σell_i}.

## Derived transport

The mass-shell relation and constants of motion yield observed energy ratio r. Differentiating M gives M'_i=-h_i M_i, and r'/r=-b with b=Σ_i h_i s_i². Thus

`(ln(det M * r))'=-θ-b`, `s'_i=(b-h_i)s_i`, and `s·s'=0`.

For W=(det M)r U0 dΩq, `W'=-(θ+b)W`. The map has Jacobian dΩs=(detM)/r³ dΩq and the energy-integrated brightness U_u(s)=r^4 U0(qhat) on interiors of transported cells. Across cell boundaries the transport PDE is weak/distributional, not pointwise classical. The discrete stored-ray model is an atomic measure, not smooth sky brightness.

`a_lm(u)=∫W Y*_{lm}(s)` with `∫|Y_lm|²dΩ=1`, Condon-Shortley. Differentiating at fixed conserved qhat:

`a'_lm=∫ W{-(θ+b)Y*_{lm}(s)+ ∇_S Y*_{lm}(s)·s'}`.

Parity from separate Cartesian axis reflections: all odd l or odd m modes vanish for this source; negative m uses `a_{l,-m}=(-1)^m (a_{lm})*`.

## Kinetic stress equivalences

`E=∫W, P_i=∫W s_i², R_ij=∫W s_i² s_j²` imply

`E'=-θ E-Σ_i h_i P_i`,
`P_i'=-(θ+2h_i)P_i+Σ_j h_j R_ij`.

`Σ_iP_i=E` and `Σ_jR_ij=P_i` enforce massless trace. Exact harmonic identities:
`a00=E/sqrt(4π)`, `a'00=E'/sqrt(4π)`,
`a20=sqrt(5/(16π))(3P3-E)` and `a'20=sqrt(5/(16π))(3P3'-E')`,
`a22=a2,-2=sqrt(15/(32π))(P1-P2)` and primed analog.

`C_l=(2l+1)^-1 Σ_{m=-l}^l |a_lm|²`, `C'_l=2(2l+1)^-1 ReΣ a_lm* a'_lm`.

## New dimensionless angular contrast observable

Define **fractional bolometric angular-energy contrast** `δ_U(s,u)=4π U_u(s)/E(u)-1`, whose sky mean is zero. For l≥1,
`C_l^δ=(4π/E)^2 C_l`, and
`(C_l^δ)' = (4π/E)^2 [C'_l - 2(E'/E) C_l]`.

This separates overall radiation dilution from normalized directional anisotropy under precisely the SAME nonthermal initial measure. Since U0 is already anisotropic, changes cannot be attributed solely to shear without an independent counterfactual.

The `C_l^δ` here is not thermodynamic CMB C_l; no blackbody spectrum, detector bandpass, Stokes data or polarization follows. GL40 is only an empirical numerical reference, not a certified continuum enclosure. This closeout reuses existing model histories; `d/du=Tstar*d/dt` and no confusion with BASS Frame::step's e-fold τ.

## Source literature used at formula level

- P. Fleury, C. Pitrou, J.-P. Uzan, *Phys. Rev. D* **91**, 043511 (2015), Bianchi-I null-ray redshift/direction mapping, doi:10.1103/PhysRevD.91.043511.
- H. Lee, E. Nungesser, P. Tod, arXiv:1911.04937, homogeneous Bianchi-I massless Einstein–Vlasov, conserved spatial covariant momenta and stress hierarchy.
- C. Pitrou, *Astropart. Phys.* **125**, 102494 (2021), collisionless/relativistic radiative intensity and multipole distribution context, doi:10.1016/j.astropartphys.2020.102494.

No independent exact continuum certificate, laboratory sky validation, or genuine distinct-author review is claimed.