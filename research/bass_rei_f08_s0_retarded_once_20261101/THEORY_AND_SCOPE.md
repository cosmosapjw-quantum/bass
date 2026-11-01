# REI-F08 S0 causal single Thomson scatter: source → observer

## Original source and assumptions
- BASS scientific parent: Draft PR317 commit 18e6273f28ea67e472c919de86594f70fd1c81c9. It contains frozen actual S0 H/He/electron history and source code. All original source hashes are checked by the imported parent.
- Original S0 source: 0.05 initial photons/H at 13.7 eV, plus 5e-15 photons/H/proper-second monochromatic injection isotropic in the **birth matter frame**. Comoving electron gas, original Verner96 H I photoelectric fit and original H/He source fractions.
- Background: metric ds² = -c²dt² + Σ a_i(t)² dx_i², a_i = exp(H_i t); constant H=(1.01,0.99,1.00)e-14 s^-1 or FLRW=(1,1,1)e-14 s^-1. Signature (-,+,+,+). Source clock 0..1e13 s. Observer at original model t_o, NOT the modern cosmic z=0.
- This is one independent continuum reconstruction using original source prescription and original frozen H/He matter history, not the original F08 discretized photon occupation. Original F08 remains HOLD and has a previously documented −6.13% photons/H discrepancy versus the independent characteristic source reconstruction; no equivalence or physical-model error certificate is admitted.

## Exact null propagation and angular Jacobian
For physical unit photon direction n_b and energy E_b at original birth time t_b, the Bianchi I conserved spatial Killing covectors are k_i=a_i(t_b) E_b n_bi. Thus
E(t)/E_b = R(t,t_b,n_b) = sqrt(Σ_i n_bi² exp[-2H_i(t-t_b)]),
n_i(t)=n_bi exp[-H_i(t-t_b)]/R.
For photon observed along n_o at t_o, with earlier scatter at t_s and D=t_o-t_s,
g=sqrt(Σ_i n_oi² exp(2H_i D)), n_si=n_oi exp(H_i D)/g, and R_out=E_o/E_s=1/g.
Map the scattering sky to the observation sky using n_o=A n_s/|A n_s|, A_i=exp(-H_i D). This gives
dΩ_s/dΩ_o = J_ang = R_out³ exp[(Σ_i H_i)D].
Energy per original comoving hydrogen nucleus per steradian transforms by J_ang*R_out; number per original H per steradian by J_ang. No point-source distance or extra bolometric scaling is inserted.

Choose right-handed e_theta and e_phi orthonormal screen at n_s and n_o. The Levi-Civita-parallel physical polarization basis obeys d(alpha)/dt = -mu d(phi)/dt with d(phi)/dt=(H_x-H_y)n_x n_y/(n_x²+n_y²). Hence with Q=I_theta-I_phi and U=2I_theta_phi, (Q+iU)_obs=exp(-2i chi)(Q+iU)_scatter, chi=int(t_s,t_o) mu dphi. The proper-time integral is numerically evaluated using Simpson; it is exact at the continuum geometric level.

## Exactly one causal first-scattered photon
Every original monochromatic S0 birth packet (t_b,n_b,E_b=13.7eV) is transported without prior Thomson interaction:
P_in=exp[-c σ_T ∫(t_b,t_s) n_e dt -c ∫(t_b,t_s) n_HI σ_HI(E(t))dt].
The original Verner96 H I photoelectric fit is identically zero below 13.60 eV. Its source and outgoing optical-depth integrals are split at the *actual direction-dependent energy threshold*, rather than sampling blindly over a discontinuity.

For unpolarized incident survived number dN_in/H, photon energy E_s, and incoming physical direction n' at t_s, the Thomson local energy gain per outgoing local solid angle and per proper second is:
G_I=(3cσ_T n_e/16π) (dN_in E_s/H) [1+(n_s·n')²],
G_Q=−(3cσ_T n_e/16π)(dN_in E_s/H)[(e_theta·n')²−(e_phi·n')²],
G_U=−(3cσ_T n_e/8π)(dN_in E_s/H)(e_theta·n')(e_phi·n').
The differential incoming photons are weighted using *birth-frame* angular quadrature and original source birth timing, not assumed isotropic after anisotropic propagation.

Outgoing energy-specific survival:
P_out(E_s)=exp[-cσ_T∫(t_s,t_o)n_e dt -c∫(t_s,t_o)n_HI σ_HI(E_s R(t,t_s,n_s))dt].
Apply P_out separately to every incoming packet energy at t_s before summing the scattering density matrix. The observer integral is
S_1(n_o,t_o)=∫(0,t_o) dt_s J_ang R_out P_out(E_s) R_screen G(t_s,n_s).
The angular Thomson normalization is exactly ∫dΩ_s (3/16π)(1+cos²θ)=1. The corresponding observer photon **number** uses J_ang without R_out. This is exactly one first-and-last Thomson collision; no incoming earlier scatter and no outgoing later scatter.

## Numerical and epistemic boundaries
- Original F08 H I and electron samples: 16,001 times, Δt=6.25e8 s, source byte-hash locked through PR317.
- Nonstationary birth integration: initial delta birth + original constant emissivity midpoint panels, birth-frame GL_mu×uniform φ. Incoming H I threshold-split Simpson. Scattering time positive Gauss-Legendre. Observer angular midpoint grid. Outgoing H I threshold-split Simpson, source-ne Thomson optical-depth and parallel transported polarization screen.
- Actual observables: energy and photon number **per original comoving H** per observed steradian, mean original birth and scattering proper times and polarized Stokes fractions. NOT an observed CMB map or standard candle flux. Observer epoch is within prescribed S0 experiment, not today's redshift zero.
- Claim ceiling: a source-prescription matched, conditionally source-H/He-matter matched, retarded first-scattered *independent continuum model*, not an exact byte or numerical replay of the original discrete F08 photon state; not full multi-scatter radiative transfer; not Einstein self-consistent; no formally proven continuum/truncation/source-model error bounds. No original accepted F05 tick161, no F09 provider binding, no original source or production mutations.
- Verify same-local-scatter limit against actual PR317, exact null/angular Jacobian, unit/Thomson gain conservation, photon positivity, FLRW null polarization, physical birth≤scatter≤observer chronology, error due to discretization and source traceability.

Primary source literature: Fleury, Pitrou & Uzan, PRD91 043511 (2015), DOI 10.1103/PhysRevD.91.043511; Pontzen & Challinor, MNRAS380 1387 (2007), DOI 10.1111/j.1365-2966.2007.12221.x; covariant polarization tensor formalism astro-ph/0412094; Verner et al. 1996 ApJ465 487, DOI 10.1086/177435.

**Drift watchdog:** This is the causal source→observer closure missing from BASS PR317. Exactly one bounded physics calculation. Stop after actual verified output and Draft backup; do not spawn adjacent source-only sky atlases. REI central 28/88 reported and BASS upper 9/15 scoped/source-mapped remain unchanged unless the original canonical source-owner admission contract is actually met.
