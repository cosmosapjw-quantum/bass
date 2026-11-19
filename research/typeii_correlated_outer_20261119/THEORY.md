# Type-II angle-frequency correlated resonance redistribution and outer-band matching

Source parent: PR #341, immutable SHA `55aa1a61ac66019f0901dd2cb02ddfdcbb5fca9c`. Original BASS main `9c6506e4e2087129a8b674ff10438e5db1a55c9d`. All changes restricted to this research directory in an isolated worktree. No original physics code or parent mutation.

## M1/C1 research contract and non-negotiable physical definitions

Metric signature (-,+,+,+). Keep h, c, k_B. Use original Type-II background at z_mean=1100, gamma_fluid=1.3, fixed source nHrest, Tm and finite n<=3 tagged-ionization fate from the source-locked parent. This is a source-conditioned tagged photon experiment, NOT self-consistent cosmological ionization or measured z=0 visibility.

Dimensionless atom-frame Doppler frequency x=(nu-nu0)/Delta_nu_D, Delta_nu_D=(nu0/c)*sqrt(2 k_B Tm/m_H). Reduced atom thermal velocity u=v_atom/sqrt(2 k_B Tm/m_H) has Maxwellian density pi^(-3/2) exp(-|u|^2). For incoming and outgoing unit directions n_i,n_o with mu=n_i.n_o, an ideal coherent-atom scattering step satisfies, to O(v_atom/c) with leading recoil,
  x_out=x_in+(n_out-n_in).u - eta_r(1-mu),
  eta_r=h nu0/(m_H c^2 Delta_nu_D/nu0).
A finite natural-width absorption weight is L_a(x_in-u_parallel)=a/[pi((x_in-u_parallel)^2+a^2)], a=A_Lya/(4 pi Delta_nu_D). The conditional parallel-atom velocity law is proportional to exp(-u_parallel^2)*L_a, normalized by its own integral. After integrating the transverse Maxwellian, x_out conditional on (x_in,u_parallel,mu) is Gaussian of mean x_in+(mu-1)u_parallel-eta_r(1-mu) and variance (1-mu^2)/2. The angle phase function is (3/4)(1+mu^2) per unit normalized sky solid-angle measure. This is a joint angular-frequency source construction, unlike PR341 factorization.

This kernel is an idealized Hummer-II-like Maxwell+Lorentz coherent atom limit, NOT the exact full natural-width, hyperfine, polarized or quantum recoil R_II kernel. A reversible pair-flux correction will be stated explicitly and checked against Wien/Bose equilibrium. Use positive finite-volume photon number on the source normal hypersurface and source D/J capacity as in PR341. Preserve angular-phase quadrature normalization.

Outer boundary matching objective: a finite inner band |x|<=Xcore and outer band <=Xouter are evolved as a single photon-count state; inner boundary crossings are diagnostic and permit reinjection. Only |x|=Xouter is terminal. Compare Xouter=40,80,120 (if runtime permits) holding initial core resolution and source time fixed. Red/blue exit at outer boundary is NOT a global escape rate.

Validation: zero recoil and LTE detailed-balance limits, angular-frequency dependence and non-factorizability, positivity/column stochasticity, count/energy+work ledger, wrong-no-J/angle-factorized/absorbing-core counterexamples, independent small matrix exponential or BDF, time/outer-size refinement, same-author hostile pass. No false production promotion.

## DAG
BASS upper: 9/15 scoped/source-mapped; newly full production nodes 0; Stage II historical 11/11 currently unproven; Join J1 0/2 FULL PASS HOLD. No auto-merge. Native subagent NOT_RUN unless available in runtime inventory.
