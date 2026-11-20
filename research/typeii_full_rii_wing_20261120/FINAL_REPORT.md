# Original BASS Type II: Hummer RII0 Voigt oracle and finite Lyman wing transport

Research completion date: 2026-11-20. Draft PR343, base PR342 SHA b23e75dcd2e8145cb161339bf08b6e1f522626f5. Source original BASS main SHA 9c6506e4e2087129a8b674ff10438e5db1a55c9d. Current branch research/bass-typeii-full-rii-wing-20261120-r1. Four theory/coding paired stages Q1–Q4. Changes confined to this research folder, no production/native HYREC code modified.

## 1. Definitions and original Hummer II derivation (derived; literature supported)

Metric signature (-,+,+,+). h=2πħ, c, k_B retained. Atom-frame line Doppler scale Δν_D=ν0 sqrt(2k_BT_m/(m_H c²)), reduced frequency x=(ν−ν0)/Δν_D, natural damping a=A_Lyα/(4πΔν_D). Define standard H(a,x)=Re w(x+ia), Voigt absorption density φ_a(x)=H(a,x)/sqrtπ with ∫φ dx=1.

For incident/outgoing photon directions with scattering cosine μ∈(−1,1), let s=sqrt((1−μ)/2), q=sqrt((1+μ)/2), S=(x+x')/(2q), Y=(x−x')/(2s). The Maxwellian atomic velocity components along n+n' and n−n' are independent Gaussians; conditional coherent emission at the atom frame fixes Y, while the Lorentz oscillator integrated against the sum direction gives H(a/q,S). Hence the original classical Hummer Type-II joint kernel is

RII0(x,x'|μ)=exp(−Y²) H(a/q,S)/(2πsq).

It is symmetric x↔x', nonnegative, and ∫dx'RII0(x,x'|μ)=φ_a(x). The conditional probability is RII0/φ_a(x). Forward μ=+1 is the Dirac distribution δ(x'−x); backward μ=−1 is evaluated by its nonsingular thermal-velocity/Lorentz integral. This is the exact original coherent atom-frame radiation-damped Doppler formula under a sharp lower level and NO recoil. Quantum recoil, fine/hyperfine, stimulated scattering and polarization are not contained in this claim.

Reference sources: D.G. Hummer, MNRAS 125 21 (1962) Section 2.2, NASA ADS https://adsabs.harvard.edu/pdf/1962MNRAS.125...21H ; Leenaarts, Pereira & Uitenbroek, A&A 543 A109 (2012) Eq(2) https://www.aanda.org/articles/aa/full_html/2012/07/aa19394-12/aa19394-12.html ; Dijkstra (2017) arXiv:1704.03416. A published HTML transcription omits an exponent square; the squared Maxwellian factor is fixed by derivation and numerical marginal normalization.

## 2. Independent CDF/Voigt/source identity (numerically checked)

Two genuinely different algorithms were executed: direct Gaussian-atom-velocity/Lorentz conditional integration preserved from PR342 and the new closed Voigt Hummer formula, including μ=−1 and far wing cases. Across x_in={2,8,20,40,80} and μ={−1,0,0.5}, a=0.001 with 96 finite frequency bins on [−120,120], the maximum finite-bin probability discrepancy is 1.0769163338864018e−14. The independent Voigt marginal integral, exact forward/back limits and nonnegative conditional bins pass. Therefore the previous velocity-integral kernel already implements recoil-free classical Hummer-II, within the chosen approximation and test domain. This is an independent analytic oracle/validation, not a newly discovered different scattering microphysics.

Static source T_m=3000.745332620248K, neutral tracer density=253341572.44286457 m−3, 6-angle×36-frequency source operator: Hummer-RII0 matrix versus parent leading-recoil operator Q differs by 7.841898374516543e−5 relative to the source global maximum rate. The no-recoil RAW generator has Wien pairwise balance residual 6.180535795036029e−4. Leading atomic recoil shift by −epsilon_r(1−μ), epsilon_r=0.0004631056690519873, is independently matched to parent leading-recoil velocity integral with maximum bin error 1.1657341758564144e−14, but the recoil-shifted RAW static Wien defect is still 6.053336880946795e−4. These are physically distinct statements: the leading-frequency shift is not a full quantum detailed-balance construction.

An EXPLICIT arithmetic pairwise thermodynamic symmetrization is applied to finite transition fluxes, yielding machine-precision Wien/Bose pair balance (e.g. shifted case 2.2751876245215988e−17), but changes the microscopic raw kernel. This reversible source Markov operator is a controlled thermo surrogate, NOT a validated full quantum recoil redistribution kernel. The finite matrix conserves photon count by column sum.

## 3. Actual Type II source time-dependent wing experiments (numerically checked)

Original BASS gamma-fluid1.3 five-state Hubble-normal Bianchi TypeII source, at z_mean=1100 over Δτ_H=0.00015. Original normal-photon frame D, angular Jacobian, positive κ and H input, inherited fixed nHrest / 1s tracer, T_m and finite n≤3 tagged-ionization fate. This is NOT re-integrated Einstein–Boltzmann–atomic dynamics. The kernel joint spectral shape is frozen at source start, while source opacity, Doppler, κ and tagged fates evolve over time. The source perturbation is dilute and not a full polarized radiation field.

A positive implicit finite-angle×frequency generator is evolved with a true outer boundary X_out in Doppler widths; internal ±20 core crossings are permitted to reinject. Scattered photons beyond the outer boundary are tracked as red/blue terminal channels without silently renormalizing the truncated spectrum. Four channels: surviving, red terminal, blue terminal and tagged ionized sum to unity with source-count defects ~1e−10. A boundary terminal is NOT global Lyman escape.

For the separately labelled thermally pair-symmetrized recoil-free Hummer-II source at 512 steps:
- Xout40: survival0.03847856464937806, red terminal0.015505247638338625, blue terminal2.5643318195555796e−6, tagged ionized0.9460136232690443, gross core return1.6651320642357494.
- Xout80: tagged ionized0.945580986367142, red terminal0.0002543270161705054.
- Xout160: tagged ionized0.9455809872302733, red terminal2.935207260523311e−7.
- Xout240: tagged ionized0.9455809875014962, red terminal3.766965796251292e−9.
- Xout320: tagged ionized0.9455809874368484, red terminal4.222815649374289e−11.

At a matched finer 1024-step source, X160 tagged ionized0.9456720766506922 and X320 tagged ionized0.9456720767660778, differing 1.1538558997159498e−10. Thus, for THIS finite model and time grid, the outer-width dependence of the tagged-ionized fraction is controlled by X160. But the X160 time512→1024 change is 9.108942041891055e−5, and the matched X40 6→14-angle change at 512 steps is −5.532068412010815e−4; both dominate the outer-boundary difference. With 14 angles, time256→512 changes tagged ionization by +1.7609849334765393e−4. No continuum-time/angle accuracy or cosmological global escape is admitted.

At X40,512 steps, replacing the exact joint raw conditional with a factorized outgoing-angle/frequency law within the same thermally symmetrized source changes the final tagged-ionization fraction by −1.0777823078456095e−10 for this particular highly opaque nearly isotropic source. This does not prove correlation irrelevant in anisotropic phase space.

## 4. Microscopic thermal-closure sensitivity (BLOCK_NOW physical claim, not a numerical bug)

With identical X40,512-step original TypeII source, RAW RII0 no-recoil tagged-ionization0.2653506010860713 versus the separately thermally symmetrized model 0.9460136232690443. The distinction is huge and is NOT within a numerical error: these are different microscopic collision operators. With leading recoil shift only and NO pair sym, source tagged ionization0.2651894894388678. Adding pairwise sym to the leading recoil kernel gives0.9460134077555259. The shift alone changes the raw source by −0.00016111164720350457; adding the explicit thermo sym changes it by +0.6808239183166581.

Conclusion: do not equate the thermodynamic pair-symmetrized finite Markov operator with exact microscopic quantum recoil RII or infer physical recombination/escape from its converged finite outer wing. The next scientific object is a source-matched full recoil/detailed-balance angular-frequency operator with actual natural-width/polarization assumptions and a separately calibrated continuum angular/time transport. An engineered equilibrium stationary state cannot by itself identify the correct microscopic kernel.

## 5. Verification, failure categories and publication boundary

Finite-source regression: six original closed-Hummer unit contracts in normal and Python -O (12 executions). Fifteen direct Maxwell-vs-Voigt and fifteen shifted-recoil independent conditional comparisons with numerical maximum <1.2e−14; source original Git blobs 9/9 exact and parent selected source blobs exactly matched. A separate BDF integration of the static finite Hummer generator agrees with Krylov matrix exponential at 3.160506361829518e−12 maximum state difference. Twelve malformed input cases rejected; scientific code contains no bypassable Python assert checks. Actual source campaigns comprise 12 base cases, 3 time/angle refinements, 1 extra 14-angle time512 case, and 3 separate leading-recoil cases. No native C/HYREC population rerun or new electron fraction/Thomson depth has been executed.

Host exact Git source archive per stage Q1–Q4 must be reverified with SHA256 and zip CRC after final commit; remote branch HEAD readback is separate. External FUSE/NTFS was blocked by ENOSPC in prior source unit despite df free ~1.8 TB; there is NO new extdrive copy or fixed root cause in this unit. No other files deleted, no mount repair executed. GitHub hosted CI only PASS if actual workflows reported; otherwise NOT_ESTABLISHED.

Reviewer: ONE BOUNDED SAME-AUTHOR HOSTILE SCIENTIFIC PASS. Native subagent not exposed, NOT_RUN. Distinct-author real blind referee NOT_RUN. Parent/main original source untouched. BASS upper DAG 9/15 scoped/source-mapped, newly full-production nodes0. StageII historical 11/11 current evidence NOT_RECOVERED. JoinJ1 0/2 FULL PASS HOLD. Production_ready=false, merge_ready=false, auto_next=false.

Next useful task: MICROSCOPIC_RECOIL_DETAILED_BALANCE_AND_ANGULAR_CONVERGENCE. Construct and benchmark the quantum/thermodynamically correct recoil-enabled full correlated RII kernel against original primary literature, then propagate angular quadrature≥14 and time refinement to a justified error budget. This is a positive physics step, not another procedural audit. Independently: recover StageII canonical evidence and diagnose external ENOSPC only with authorized access.
