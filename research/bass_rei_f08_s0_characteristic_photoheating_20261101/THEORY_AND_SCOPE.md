# BASS → REI F08 S0 source-preserving characteristic photon microphysics

UNIT: BASS_REI_F08_S0_CHARACTERISTIC_PHOTOION_HEAT_20261101
SCIENCE STATUS: exploratory/source-conditional, original coupled REI production HOLD.
PARENT: BASS PR321 exact 178d93c380a0e868a22869c3160d81c0aa643098, source from BASS PR317 and original REI F08.

## Original assumptions and source
Metric (-,+,+,+), ds²=-c²dt²+Σa_i(t)²dx_i²; a_i=exp(H_i*t), H_BI=(1.01,0.99,1)*10^-14 s^-1, FLRW=(1,1,1)*10^-14 s^-1, t=0..10^13 proper seconds. Original S0 is 13.7-eV monochromatic isotropic-in-birth-matter-frame photon source: 0.05 photons/H initially and 5e-15 photons/H/s thereafter. Use original F08 saved 16,001 H/He proper matter samples and the same 128 original q direction labels. Original HI proper density is n_HI(t)=n_H(t)(1-x_HII(t)), frozen to the source-owner history; do not re-evolve chemistry or temperature and do not import F05/P19 rates.

Original BASS parent retains exact checkpoint SHA4/4, original physical source SHA12/12, original Verner96 neutral HI photoelectric fit. Verner photo-fit cutoff E>=13.60 eV and the distinct original chemical H I binding energy χ_HI=13.598434599702 eV are kept separate. Original photon-owner F08 has a fixed 17-node energy hat and a known original monoenergetic support violation. The new solution retains every birth energy instead of projecting onto fixed nodes.

## Exact source-level characteristic derivation
For original conserved q_i direction labels define
g(q,t) = [Σ_i q_i² exp(-2 H_i t)]^(1/2).
A 13.7-eV photon emitted at t_b has physical energy E(q,t;t_b)=13.7 eV * g(q,t)/g(q,t_b).
Thus d ln E/dt = -Σ_i H_i n_i(t)², verified using Wolfram. The physical support floor is E>=13.7 exp(-H_max*t). Every birth packet remains countable after cosmological redshift beneath the HI photo-fit threshold, while no such packet can generate photoionization then.

Original source angular measure on q is w_d(t_b) proportional to exp[-Σ_i H_i t_b]/g(q_d,t_b)^3, normalized across actual 128 discrete q rays for each birth; at t_b=0 it is exactly 1/128.
Define photon number measure per original H dB(q,t_b)=(0.05 delta(t_b)+5e-15 dt_b)*w_q(t_b).
The original physical absorption rate is
λ_HI(t;q,t_b) = c n_HI(t) σ_HI(E(q,t;t_b)) [s^-1].
Its first-order photon collision survival is S(t,t_b)=exp[-∫_(t_b)^t λ_HI(t')dt'].
The integration is split at the direction-dependent characteristic crossing E=13.60 eV; below this the frozen cross section vanishes, but the photon persists in number/energy.

The HI photoionization rate per neutral HI atom (s^-1) is
Γ_HI(t) = c n_H(t) ∫dB S(t,t_b) σ_HI(E(t)).
The photoionization event count rate per original H nucleus is
dA_HI/dt = c n_HI(t) ∫dB S σ_HI(E(t)) = [1-x_HII(t)] Γ_HI(t).
The photoelectron excess heat rate (eV/original H/s) is
dQ_photo/dt = c n_HI(t)∫dB S σ_HI(E(t)) max(E(t)-χ_HI,0).
Cumulative absorbed count and energy are obtained along each photon trajectory, including its actual absorption-event energy E(t_abs) rather than the 13.7-eV birth energy.
The photon-number and energy ledgers are
N_birth=N_survive+N_abs,
13.7 eV*N_birth = U_survive + U_abs + W_redshift.
And E_abs=χ_HI*N_abs+Q_excess at the implemented per-panel physical energy quadrature accuracy.

## Physics calculations and model comparison
A. SOURCE_EXACT_CHARACTERISTIC: same original S0 birth measure q,t_b; redshifted E carried off-grid, split photoabsorption at threshold; original n_HI(t), no chemistry backreaction.
B. ORIGINAL_FIXED_HAT_FROZEN_HI: replay the original 16,000-step q/17-energy-node hat suboperator and original source angular weights plus fixed original HI implicit absorption, previously checked under PR321; compute rates and photoelectron heat from its actual surviving spectral bins.
C. ORIGINAL_OWNER_F08_OUTPUT: source archived gamma_HI_per_s, photon_n, absorbed_n, photon_u and H/He matter temperature are separate data. Do NOT call native F08 thermal_work_ev_per_h identical to photoelectron heat; it includes other gas and expansion contributions.

Compare Γ_HI, HI event rate, instantaneous excess photoheat rate, cumulative photoelectron heat, absorbed photon number and redshift energy work at each of 15 source-accepted time ticks for both actual S0 Bianchi I and FLRW histories. New data are real physically computed source-conditional ionizing-photon histories, not new CMB or observer sky atlases. Original F08 discrete packet occupation, nonlinear MPRK/SDIRK gas root and original ionization IVP are NOT replayed.

## Scientific claim ceiling and validation
Source byte locks and source-owner identity are nonnegotiable; original F08 photon state/source admission remains HOLD. Normal and optimized unit tests, exact null support, no opacity control, no negative photon/heating, original Verner fit parity, original source-gamma vs fixed-hat, ray-to-history sums and number/energy ledgers must pass. A separate same-author readback checks all output values and physical causal limits. Source-birth GL and absorption midpoint-Simpson settings are numerically checked but are not formally certified global errors. Do not equate these differences to a changed coupled H/He IGM history or full original source acceptance.

The original source model has Hubble parameters prescribed, not Einstein-constrained; no full multi-group H+He exact radiation-chemistry feedback. The original F08/REI F05 tick160->161 admission and F09 provider-domain remain separate central science blockers. Central REI canonical 28/88 reported delta0; Working 33/88 nonadditive; Physical Fast 4/7; BASS upper 9/15 scoped/source mapped, delta fully complete0. No merge, no production mutation, no force push, no tolerance relaxation, AUTO_NEXT=false.

Literature: Verner et al., ApJ 465 487 (1996), DOI 10.1086/177435, photoionization fit. Fleury, Pitrou and Uzan, Phys Rev D 91 043511 (2015), DOI 10.1103/PhysRevD.91.043511, exact Bianchi I null geodesics. All specific source constants and actual results are from original REI inputs and the physics model, not inferred from external literature.
