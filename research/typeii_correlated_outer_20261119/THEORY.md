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

## M2/C2 original finite joint-kernel science result

The original source-conditioned coherent-atom Maxwell/Lorentz kernel (not exact full R_II) yields E[xout] at x_in=2 for mu=+1,0,-1: 2.125 bin-centre, 0.0153541435, -2.00639269. The first entry is bin-centre quantization. The finite static 6-angle x36-frequency matrix has shape [216, 216]. Joint raw vs independent angle-frequency conditional L1 gap is 1.22829264044. Thermodynamic pairwise symmetrization produces Wien pair and nonlinear induced BE reciprocity with defects 1.87e-16 and 1.11e-16; column number conservation relative defect 3.22e-16. Source rates depend on the declared fixed T=3000K,nl=2.5e8m^-3. The symmetrization changes the raw coherent-atom conditional distribution and must not be misrepresented as exact Hummer R_II. No global line escape or coupled radiation/atom solution.

## M3/C3: actual time-dependent BASS source and finite outer-band return experiment

The immutable original BASS gamma-law Type-II source supplies H(tau_H), normal-photon kappa, Doppler D, n_Hrest, trace 1s density, T_m, and finite n<=3 tagged ionization fate. The positive implicit source propagator uses the 6-angle joint coherent-atom kernel whose normalized shape is fixed at zmean1100; actual scattering hazard, damping through source T_m, D/H, tagged ionization and directional drift change over time. This is a stated frozen-kernel-shape approximation and is not a full evolving RII. Simulation duration delta tau_H=0.00015, ending zmean=1099.83486239. Original input tagged Gaussian center+3 width3 Doppler units with an isotropic atom-frame source-angle profile.

- core_20: survival=1.0282421737e-09 red-terminal=0.276898487728 blue-terminal=0.268993188815 ionized=0.454108322563 gross core outward=0 gross core return=0, count defect <=1.36e-10.
- outer_40: survival=0.0389515667971 red-terminal=0.0163799908498 blue-terminal=0.000890256831996 ionized=0.943778185606 gross core outward=1.70289960278 gross core return=1.65729037253, count defect <=1.25e-10.
- outer_80: survival=0.0554359419653 red-terminal=0.000262131377202 blue-terminal=2.33891490938e-25 ionized=0.944301927036 gross core outward=1.70435659691 gross core return=1.65938743757, count defect <=3.79e-10.
- outer_40_factorized: survival=0.0389515663752 red-terminal=0.0163799908271 blue-terminal=0.000890256829366 ionized=0.943778186194 gross core outward=1.70289960412 gross core return=1.65729037431, count defect <=2.26e-10.
- outer_40_frozen: survival=0.0388940648939 red-terminal=0.0163758803715 blue-terminal=0.000890095830595 ionized=0.943839958847 gross core outward=1.70242778855 gross core return=1.65685365388, count defect <=5.76e-11.
- outer_40_time128: survival=0.0381575181719 red-terminal=0.0164402556574 blue-terminal=0.000893496375101 ionized=0.944508730087 gross core outward=1.70471110494 gross core return=1.65959638007, count defect <=2.91e-10.

Gross crossing integrals may exceed one due to repeated scattering and do not represent one-pass probabilities. An internal ±20 Doppler halfwidth treated as absorbing artificially loses reinjecting trajectories; crossing probabilities become terminal only at the declared outer boundary. Results at X=20/40/80 are DIFFERENT finite-domain boundary conditions, not a globally converged Lya escape factor. This is a conditional tagged-photon study; no new cosmological x_e, fully coupled photon-gas energy/charge, or observed CMB. The finite static joint kernel has explicit thermal symmetrization; its raw angle-frequency L1 gap from the factorized conditional is large, but the saturated terminal probabilities in this particular nearly isotropic source are close. The gap is not by itself a measured CMB effect.
