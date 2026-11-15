# BASS to REI F08 | Original 160-consecutive-step interval propagation and physical support witness

Status: DERIVED + ORIGINAL_RUST_IMPLEMENTATION_VERIFIED + NUMERICALLY_CHECKED_SCOPED; PHYSICAL_SUPPORT_FAIL; OWNER_ADMISSION_HOLD.

## Frozen authority and run

- Original BASS PR #331 head b2562f6be2076c985eea50d871de9c49d8588a06; parent #328 b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6.
- REI original paired_runtime.rs SHA-256 b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7, coupled_primary.rs SHA-256 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b.
- Original F08 photon source pair SHA-256 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8; no owner source mutation.
- Original energy-node PairedConfig: spectral_subdivisions=4, n_mu=8, n_phi=16. Photon birth energy 13.7 eV; initial photon count 0.05/H; source 5e-15 photons/H/s; proper dt 625000000 s; Bianchi H=(1.01,0.99,1)*1e-14 /s, matched FLRW H=(1,1,1)*1e-14 /s; 160 consecutive stages per geometry.
- BASS-only Rust adapter uses unaltered original paired_initial, paired_trial, primary_stage_root, primary_stage_step_conservative and Interval. Only exports paired_runtime in a temporary copy outside Git; source bytes frozen.

## Derived physical support lemma

For diagonal Bianchi I with constant nonnegative directional Hubble rates, a photon born at proper time t_b with physical energy E_b and nonzero canonical q obeys
E(t;q,t_b) = E_b [sum_i q_i^2 exp(-2H_i t) / sum_i q_i^2 exp(-2H_i t_b)]^(1/2).
The derivative is d(log E)/dt = -sum_i H_i w_i(t), with w_i=q_i^2 exp(-2H_i t)/sum_j q_j^2 exp(-2H_j t), w_i>=0 and sum_i w_i=1. Thus for t>=t_b>=0,
E_b exp[-H_max(t-t_b)] <= E(t;q,t_b) <= E_b exp[-H_min(t-t_b)].
All initial photons and newly sourced photons are born at 13.7 eV, with no new photon emission energies in this original selected model. Every surviving photon at t must therefore have energy >= E_min(t)=13.7 exp(-H_max t). Photoabsorption removes photon number, not transfers photons to lower energy bins.

The adapter computes a conservative lower E_min using the original outward interval exp and multiplication for the fixed source binary64 H/t. It then counts photons on fixed original energy nodes strictly below that lower threshold, including their interval lower mass.

## Actual results and status

Original paired_runtime 160/160 consecutive stages PASS original numerical local (<2e-4), public width (<2e-3) and point ledger (<=1e-12) gates in each S0 geometry. The state gas and photon interval boxes are carried between successive native paired_trial calls.

At step160 (t=1e11 s), Bianchi I carries 0.017768085382252993 photons/H, 41.99203797501811% of surviving photons, on forbidden nodes below physically rigorous E_min 13.686169985332945 eV. The interval lower photon mass on forbidden nodes is 0.017768084974620145 photons/H >0. FLRW carries 0.017768182757601163 photons/H, 41.99226855533323%, and lower box mass 0.0177681823499538 photons/H below E_min 13.686306847717109 eV.

The result is a positive native numerical and interval evaluation in an intrinsically support-inaccurate discrete model, and a negative physical-source-support result. It does NOT constitute global continuum interval validation or a failed Krawczyk theorem. The original runtime lacks full original F08 14 production ledger interval propagation and does not propagate birth energy/q/angular/atomic cross-section intervals. Pointwise cumulative conservation and selected interval boxes do not close these obligations.

BASS PR328 had 0.4201835222 fixed-hat unsupported fraction on its distinct native packet source-prescribed model: do not numerically conflate with paired_runtime's 0.4199203798.

## Watchdog and handoff

- NUMERICAL_STAGE_INTERVAL_PROPAGATION: PASS under the fixed-hat discrete model for 320 total stages.
- PHYSICAL_13.7_EV_SOURCE_SUPPORT_PRESERVATION: FAIL; strictly positive forbidden-node interval mass.
- GLOBAL_BIRTH_ENERGY_ANGULAR_Q_INTERVAL_CERTIFICATION: NOT_RUN.
- ORIGINAL_F08_FULL_PHOTON_HHE_THERMAL_14_LEDGER_ACCEPTANCE: NOT_RUN, HOLD.
- REI central 28/88 reported; Working 33/88 nonadditive; Physical Fast 4/7; BASS upper 9/15 scoped, no new accepted full node.
- Next: interval-capable source-support-preserving characteristic photon packets (energy, angular q and number), coupled to original gas implicit root and full source owner photon/HHe/thermal ledgers under unchanged acceptance.
- No merge, force push, source owner mutation, tolerance relaxation, production or automatic next cycle.
