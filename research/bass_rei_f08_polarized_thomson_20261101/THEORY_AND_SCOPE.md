# BASS × REI F08: source-electron-matched Thomson polarization, first-order test-radiation model

**Research unit:** BASS_REI_F08_POLARIZED_THOMSON_TEST_RADIATION_20261101.
**Scope:** one bounded new science unit, an electron/geometry-matched polarization response. No original REI F05/F08/F09 state mutation; no REI source-owner equivalence for the *photon field*. Not a replacement for BASS KM2N/PR313.

## Original scientific dependencies (typed)
- REI original source owner: \`cosmosapjw-quantum/rei_bianchi\` PR349 HEAD \`1605236b8172db411d862caa219322d6af6953b1\`. Original F08 paired S0 BI and FLRW histories each 16,001 rows; scientific_admission=HOLD; original F05 26-event first coupled interval at 160/131072 BLOCKED; F09 external atomic provider BLOCKED.
- Source-pair identity: SHA256 \`0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8\`. Source original S0 electron CSV SHA256 BI \`663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723\`, FLRW \`0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa\`; exact original scenario SHA \`c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1\`.
- REI S0 true photon source is an isotropic 13.7-eV continuous-injection monochromatic field, **NOT** the test Planck radiation used below. We do not assert original photon source matching or original ionization/thermal IVP rerun.
- BASS source context PR313 \`bb0a6565ca6dea96b4605ede8f155d7f9ed5b02a\` is an independently sourced Peebles/P8 Ly-alpha first-scattered electron-history tangent. Its source geometry/clock is **NOT** identified with REI F08. We do not transplant its numerical values.

## Definition and derivation
Signature \`(-,+,+,+)\`, physical cosmic proper time \`t\` [s]; \`ds²=-c²dt²+sum_i a_i²dx_i²\`, \`a_i(t)=exp(H_i t)\`, \`H=(1.01,0.99,1.00)×10^-14 s^-1\` and \`Hbar=10^-14 s^-1\`. Comoving electrons, no peculiar tilt. \`sigma_ij=diag(H_i-Hbar)\`, trace zero. \`c=2.99792458×10^10 cm/s\`, \`sigma_T=6.6524587051×10^-25 cm²\` (original REI owner).

Assume an **external mathematical test radiation**: initially isotropic unpolarized Planck phase-space distribution at original \`t=0\`, free-streaming up to its first Thomson interaction. It is not identified with source-owned S0 injected photons, primordial CMB, or an observed radiation spectrum. Spatial covectors \`k_i\` conserve along Bianchi I null geodesics. For physical photon direction \`n\` at time t:
\`E_0/E_t = sqrt(sum_i exp(2H_i t)n_i²)\`.
Thus its local equivalent thermodynamic temperature obeys
\`T(n,t)=T_initial/sqrt(sum_i exp(2H_i t)n_i²)\`
and \`Theta(n,t) = -t sigma_ij n_i n_j + O((sigma t)²)\`, relative to the isotropically redshifting Planck mean \`Tbar(t)=T_initial exp(-Hbar t)\`. The temperature anisotropy is dimensionless; \`Theta\` is quadrupolar because \`tr sigma=0\`.

Cold Thomson electron-rest-frame density-matrix redistribution of unpolarized incident \`Theta\`:
\`dI_AB/dtau=(3/(16pi)) int dOmega' Theta(n') [delta_AB-(e_A·n')(e_B·n')]\`.
Using \`int n'_i n'_j n'_k n'_l dOmega=4pi/15(delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk)\`,
\`dI_AB/dtau = (t/10) sigma(e_A,e_B)\` for its anisotropic part. Define Stokes \`Q=I_theta,theta-I_phi,phi\`, \`U=2I_theta,phi\`, and \`m=e_theta+i e_phi\`.
The first nonzero polarization at observer \`t_o\` is therefore

\`(Q+iU)/Tbar = [c sigma_T / 10] int_0^{t_o} n_e(t) t dt × sigma_ij m^i m^j + O((sigma t)^2,tau^2)\`.

This is the **first collision source** in thermodynamic-equivalent Stokes convention, not an all-orders radiation solution. The observer screen is held fixed at zeroth shear: its directional drift/parallel rotation enters higher order in shear for this initially unpolarized field. The underlying exact Bianchi I source redshift (from \`a_i\`) is used in the derivation, not replaced by isotropic redshift.

Piecewise-linear interpolation on original 16,001 REI time samples is integrated **analytically per panel**, rather than replacing source values or solving a new H/He IVP. For \`n_e(t_i)=p, n_e(t_i+h)=q\`:
\`int_{t_i}^{t_i+h} n_e dt = h(p+q)/2\`;
\`int_{t_i}^{t_i+h} n_e t dt = h[t_i(p+q)/2+h(p/6+q/3)]\`.
The output records \`tau=c sigma_T int n_e dt\`, \`K=(c sigma_T/10)int n_e t dt\`, and \`(Q,U) = (K(sigma_thetatheta-sigma_phiphi),2K sigma_thetaphi)\`.

## Controls and scope-matched hostile review
1. FLRW \`sigma=0\` gives strictly zero Stokes field despite \`n_e>0\` (exact algebraic control).
2. \`n_e=0\` gives zero; scaling \`n_e\` by 2 gives exactly doubled linear-order response.
3. For north-pole \`e_theta=x,e_phi=y\`, \`Q=K(sigma_x-sigma_y)>0\`, \`U=0\`. Under rotation of the polar screen by \`phi\`, \`Q+iU\` transforms with spin-two phase \`exp(-2i phi)\` under our oriented basis choice.
4. Direct *unreduced* Thomson incoming-angle quadrature independently checks the analytic 1/10 coefficient; 128×256 grid relative max component discrepancy \`3.2596253074468535×10^-9\` for one nontrivial sky direction, compared with the model's linear shear source.
5. Same source \`n_e\` sampled every 16th point changes \`K\` at the final endpoint by \`2.598038673085057×10^-9\` relative; this tests only interpolation/quadrature, not physical model error.
6. Conditional source material control: use original FLRW and BI \`n_e\` on *the same* BI metric (not a second observed universe). Final \`K_BI/K_FL-1=2.148425428671885×10^-7\`.
7. Largest \`|sigma_i t|\` in the source interval is \`10^-3\`; \`tau(t_end)=1.854154317787376×10^-5\`. Omitted second-order shear and multiple-scattering terms are **not** rigorously bounded by the grid tests. No astrophysical IGM/CMB observational fit, no source spectral absorption, no source H I photoionization transfer, no electron temperature/Klein–Nishina, no Einstein self-consistency or rate provider certification.

Adversarial scientific decision: this is a real REI F08 *electron-geometry matched* BASS polar scattering operator with 10,752 computed ray outputs; its initial photon field is externally stipulated, so it does **not** certify a fully source-matched REI physical polarized sky or complete an original BASS KM-2/OB-1 or central REI node. It must not be used as a Planck CMB prediction. The earlier BASS PR313 source-Peebles and REI-F08 domains remain scientifically non-equivalent. User mission critical path remains REI original F05 first accepted coupled interval, F09 source-domain admission, then source-matched full photon polarization.

## Literature
- Pontzen and Challinor (2007), *MNRAS* 380, 1387, DOI 10.1111/j.1365-2966.2007.12221.x, Bianchi polarized Boltzmann transport and Thomson quadrupole.
- Fleury, Pitrou and Uzan (2015), *PRD* 91, 043511, DOI 10.1103/PhysRevD.91.043511, exact Bianchi I null redshift/direction and Sachs optics.

**Research status:** DERIVED; CAS coefficient checked in Wolfram; 12/12 ordinary+12/12 optimized direct unit/source tests; numerical source-data generation tested; same-author hostile review, not a distinct-author blind referee. Production HOLD; no merge or REI mutation.
