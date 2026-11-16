# TypeII evolving redistribution and phase-space transport: final scoped report

Draft PR340. Frozen parent PR339/0577ef0a40cf10130a5933eb52c7230d4de1f11b. Four local phases P1-P4; upper DAG9/15 scoped/source-mapped, new full upper nodes0. The unit is bounded implementation+source experiment+claim disposition, not full correlated line transfer or production readiness.

## Main scientific construction
Original BASS homogeneous TypeII source angular flow yields div_S2 n'=3Sigma_nn. Transported sky Jacobian J obeys J'=3Sigma_nn J; V=exp3DeltaTau and nu_normal yield the exact collisionless V nu_normal^3 J invariant. Normal-comoving photon counts in atom-frequency bins require M=V w_normal D^-3 g_nu (g_nu includes the nu² density of states), with D=Gamma(1-beta n_y). Thus correct local collision path factor D/H_n and the normal-slice measure are treated consistently. This is not the original26-ray set relabeled as a quadrature: actual GLmu x periodicphi rules are transported.

Original401 source-state gap=5.5511151231257827e-16; phase invariant defect=1.2656542480726785e-14. Neighboring-ray independent area-Jacobian relative gap=5.4269955196417641e-10; normal radiation stress-energy derivative gap=1.8143842532230763e-11. The long source interval zmean1700..300 focuses angular structure: area errors32/128/512/2048/4608 directions are0.192858/0.0171956/0.000133525/4.016e-8/6.891e-12. Per-ray invariance alone does not certify a coarse sky integral. Full-interval integrated comoving radiation energy converges to0.237651709099295 of the initial value, in this fixed source geometry.

## Collision model actually implemented
Leading angle-averaged frequency Fokker-Planck diffusion/recoil is combined ADDITIVELY with elastic unpolarized dipole angular redistribution. This factorization is explicit, not full R_II(angle,frequency;angle',frequency'). The reversible adjacent-frequency Bose flux satisfies thermal detailed balance and nonpositive pair free-energy derivative. Actual source trajectories use its dilute tagged-photon limit, with nu² density of states, positive implicit M-matrix frequency updates and exact angular semigroup. Source resonance rate, temperature and finite-cascade tagged ionization probability evolve in time. No continuous emission/atom feedback is solved.

Independent complete192-variable static collision generator plus loss counters agrees with the split implementation under timestep refinement. Implicit frequency evolution and upwind remap are first order; no global second-order or rigorous error-bound claim. The spectrum is a smooth3-Doppler-width injection, with finite absorbing red/blue band boundaries.

## Actual source measurements
23 primary source histories ran, plus a preliminary pilot. Each starts with one tagged photon per reference normal-comoving m3 and remains extremely dilute. A finite duration DeltaTau=0.003 is used. At zmean1100, half-band20 initial Doppler widths,80frequency cells,32angles and1280 time steps:
- surviving=6.2380524635830372e-106
- red band exit=0.30339008972520837
- blue band exit=0.28800474558710559
- tagged ionization=0.40860516471840752.
Time refinement640->1280 changes the largest outcome by3.773103868592864e-5; these digits are reproducible numerical outputs, not precision-physics significant figures. Frequency80->160 at640 steps changes the largest fraction by5.8559021637871744e-6. Angular32->72 at320steps changes it by5.021816296135739e-12 in this short interval. The long-interval sky test above needs much higher resolution and is not contradicted by this local angular convergence.

At the SAME320-step comparison level, bands20/40/80 Doppler halfwidth give (red,blue,ionized):
20: 0.30350567535348111, 0.2878973838050764, 0.40859694091326304;
40: 0.086332100060270311, 0.066221344112585193, 0.84744655573365246;
80: 0.023712699461605452, 0.0040064409082722604, 0.97228066942420543.
The80-width case retains1.9009074185051866e-07 inside at the endpoint. Finite-band exits drastically change when the boundary moves and are NOT a global escape probability or the same physical domain. The Gaussian injection's omitted initial tail is negligible at20 widths; the observed difference reflects transport/return possibilities excluded by narrower boundaries, together with the declared absorbing-boundary model.

Without frequency diffusion at20width the ionized fraction is0.715882062504643 instead of0.408596940913263 in the matched320-step run. Without recoil the red outcome falls to0.299356178008737 from0.303505675353481. Frozen-material comparisons retain actual evolving geometry but freeze T,n_lower and p_ion: at z1100/640steps the ionized fraction increases by1.46136533734e-5; its paired effect changes by2.8717e-7 on320->640 refinement. At z1700 the frozen/evolving paired effect is about2.72527e-4 at640steps, with paired-effect change1.36295e-6 on refinement. Absolute z1700 red-fraction discretization shifts are larger than that paired effect, so paired sensitivity is not advertised as a precise absolute solution.

Maximum packet-number ledger gap=8.8515261786881183e-10; resolved normal-radiation energy boundary+ionization+exchange+geometric-work gap=8.8460966665308506e-10. These are numerical accounting checks, not closure-accuracy estimates. Frequency exchange heat is read from edge currents; angular scattering has zero atom-frame elastic energy change but normal-frame momentum/work exchange. Neither feeds back on the matter reservoir.

## Verification and genuine repaired defects
16 contracts ran normally and under Python-O:32 executions.16 malformed inputs reject. Four optimized command replays include TWO actual source packet runs, phase/measure checks, complete-generator check and analysis; nine selected output files reproduce byte-exact. Every stored actual-source output triplet is hash-checked. Original BASS9/9 blobs and parent input Git identities remain exact. One same-author hostile pass was performed, not a blind/distinct-author referee; no native subagent.

The initial512-direction full-interval area target failed because angular focusing was unresolved. Refinement to4608 preserved all physical formulas/tolerances and passed. A separate zero-time API readout omitted death_energy_J; a RED regression was recorded and repaired by returning zero for that field. All positive-time science outputs stayed unchanged.

Wrong frozen angular weights create a photon-number defect2.5061513753 over the full interval; correct phase measure conserves number. Replacing normal-slice weights by atom-rest-slice weights leaves a nonzero stationary residual0.02804825619 in the specified angular control. Using atom reaction time in place of photon path time has3.14149% max relative error in the z1100 directional control. Omitting recoil breaks Wien equilibrium. Treating total resonance interactions as true tagged ionization overcounts that instantaneous loss by1.3796951e7 at z1100.

## Claim gate and next work
Admit derived homogeneous source phase-space measure, verified finite-volume/angle kernels, and actual evolving finite-band tagged histories in the declared factorized closure. Not admitted: exact joint angle-frequency resonance redistribution, stimulated nonlinear field evolution, far-wing return/global escape, population/thermal/momentum/Einstein backreaction, new native HYREC xe/tau or CMB observations. Smooth-spectrum FP and unpolarized assumptions remain physical limitations even when discretization converges.

Next unit: ANGLE_FREQUENCY_CORRELATED_RESONANCE_REDISTRIBUTION. Construct a source-grounded joint thermal-atom frequency/direction kernel and compare its moments and tagged output against this factorized baseline before coupling line populations or a global escape observable. Independently retain StageII canonical evidence recovery and owner-authorized external-backup repair.

## Preservation
P1-P4 are separately committed/pushed and host-archived. No external-disk write is attempted: parent ENOSPC remains unresolved and user files/storage configuration are untouched. Thus GitHub+host preservation succeeds; an external redundant copy is NOT verified in this unit. Parent/main remain unchanged. Production_ready=false, merge_ready=false, auto_next=false; StageII historical11/11 current canonical unestablished; JoinJ1 0/2 HOLD.
