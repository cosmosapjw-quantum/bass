# BASS → REI F08 S0 | Continuous original-Rust photon/HHe/thermal science

2026-11-02 | RESEARCH ONLY | Original REI owner admission HOLD.

## New genuinely continuous physical result
The earlier source-scoped BASS PR326 executed 20 original native Rust H/He stages from independent frozen F08 gas parents. This research adds ONE actual *continuous* source-prescription-matched photon+H/He+thermal IVP: each coupled model's previous photon survivors AND gas fractions/thermal/escaped energy are carried to the next original source proper timestep. Two original cosmological backgrounds (Bianchi I and FLRW) × two photon energy representations (exact 13.7 eV birth-energy characteristic, original 17 fixed-bin hat and low-energy guard) ×160 consecutive original F08 proper steps (625000000 seconds each) = 640 actual native Rust coupled gas+photon states and 320 paired physical response rows, from t=0 to t=1e11 proper seconds.

Original owner photon source S0: initial 0.05/H at 13.7 eV, continuous 5e-15 photons/H/s at 13.7 eV, original 128-q angular sky, original source birth weights exp[-sum H_i*t]/g(q,t)^3, original neutral H/He/He+ atomic cross-section fits. Original Hubble Bianchi I H=(1.01,.99,1.00)e-14 /s or matched FLRW H=(1,1,1)e-14 /s. Original gas initial fractions HII=.9,HeII=.3,HeIII=.6, Tgas=50000 K, nH0=1e-4 cm^-3, fHe=.083 and proper density evolution. Metric (-,+,+,+), c=29979245800 cm/s, kB=1.380649e-16 erg/K. Original StepControl(200,1e-15) UNCHANGED. All original rust 51/51, F08 S0 source 12/12, native photon checkpoint 4/4 source SHA256 locks PASS, all original authoritative source files byte-exact. New BASS-only Rust packet adapter calls unmodified original Rust primary_stage_step_conservative; parent BASS PR326 exact HEAD 4984b42a9ed4025e4b3f20a3a61355a448e522ab. The original REI owner/production and BASS main source remain untouched.

## Causal equations and numerically executed physics
Each S0 photon packet has original q and born 13.7eV. E(t;t_b,q)=13.7 sqrt(sum_i q_i² exp[-2H_i t]) / sqrt(sum_i q_i² exp[-2H_i t_b]).
At every step:
(1) redshift surviving photons along exact Bianchi null rays (or native source-fixed hat grid remap + preserved below-10eV guard);
(2) inject true original S0 photons on 128 q with original source-normalized weights at new proper clock;
(3) invoke the actual original Rust coupled chemical/thermal backward implicit stage with native HI/HeI/HeII absorption, collisions/recombination, photoelectron heating, expansion work and atomic binding;
(4) carry that same model's newly evolved gas and surviving photons to the next original step. No resetting from original F08 saved gas after step1.

Original astrophysical number/energy cumulative identities:
N_birth(initial+source)=N_surviving+N_photoabsorbed;
E_initial_total+13.7eV*N_new_emitted=E_final_total+W_redshift+W_thermal;
E_total=w+chiHI*xHII+fHe*[chiHeI*xHeII+(chiHeI+chiHeII)*xHeIII]+escaped+sum E_photon*N_photon.
Per-stage native HII event identity: dxHII=photoHI+collisionalHI-recombinationHI.
Actual original native Root max residual=2.587264649414666e-16, maximal independent HII identity residual=1.8430383683179612e-16, max cumulative photon-number residual=3.95516952522712e-16/H, max cumulative energy residual=1.4210854715202004e-14eV/H.

## Actually measured physical response: original Bianchi I, continuous source
| Original source tick | t proper s | Characteristic minus hat xHII | Characteristic minus hat temperature K |
|---:|---:|---:|---:|
| 1 | 6.25e8 | -3.194000619544113e-12 | +1.6419653547927737e-7 |
| 16 | 1e10 | -4.0420833347099006e-10 | +2.131843939423561e-5 |
| 32 | 2e10 | -6.566909238614471e-10 | +5.999337008688599e-5 |
| 64 | 4e10 | +3.213777244326366e-8 | -0.0005915827350690961 |
| 96 | 6e10 | +2.801434930699287e-7 | -0.006237325753318146 |
| 128 | 8e10 | +1.152183910724247e-6 | -0.02644624783715699 |
| 160 | 1e11 | +3.290156078139539e-6 | -0.07615267288929317 |

At original tick160, characteristic xHII - source saved original F08 xHII=+3.4016409689030525e-7 and fixed-hat - original=-2.9499919812492337e-6; this means source-conditional characteristic is closer to this recorded metric but DOES NOT prove it is a more accurate solution to the original owner interval-certified solver. The two models have different historical remaining photon numbers, not only instantaneous frequency shape. FLRW reaches a comparable +3.2897084959460088e-6 xHII and -0.07614218963863095K T delta.

## Independent review and verification
- Original source 51 Rust +12 S0+4 native checkpoint = 67/67 SHA256 exactly. Source/branch original Rust coupled_primary.rs 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b, original Verner atomic_provider.rs b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3.
- Rust original stage built release, all 640 actual native calls succeed; same-author stdlib independent data-level source/physical audit PASS. Python normal 14/14 and python -O 14/14 tests PASS. Self-adversarial checks include original source headers, causal null energy bound, initial condition parity with parent PR326 first native one-step, actual original source S0 reference curve first160, photon count, chemical HII and gas+photon energy budgets, helium physical domain and per-model self-generated previous state.
- Cold proper 64-step replay independently executed across all 4 physical background/model combinations (256 new physical state rows) and its full prefix agrees with the 160-step model. This is a prefix reproduction check, **not** global time-step convergence; original dt remains fixed, time-refinement not performed. Upper time horizon is 160 original source steps, not original full 16,000 step or F05 26event/OTS.
- Output source science rows: 640 source-conditional native gas+photon trajectories, 320 model difference responses. Two scientific plots as PNG/SVG. Original source owner scientific acceptance remains HOLD, no full 14-ledger MPRK22/SDIRK2 interval enclosure.
- Native Rust scoped example first-stage is true unchanged source-owned primary_stage_step_conservative, but this wrapper is a new BASS driver and not the source owner paired_runtime itself. Original material reset happens ONLY at t=0. Source photon histories are self-consistently coupled to the gas after t=0, **not** Einstein-constrained Bianchi geometry nor observationally calibrated IGM.

## Drift watchdog and original REI IGM mission gate
This is a strictly new constructive physical result beyond PR326 one-step F08 parent-state tests, not process-only metadata, sky atlas, spectral opacity tables, or performance optimization. New continuous physical rows and closure are the objective science outcome. However it is a **research-experimental source-prescription-matched independent IVP**, not the original REI source-owner production/acceptance. Its 160 steps are much shorter than original F08 16000-step prescribed horizon and are NOT the distinct F05 accepted tick160/131072 physical domain. Do not conflate two source-owner tick counters.

REI canonical reported 28/88, delta0. REI working 33/88 nonadditive, physical fast 4/7 reported, BASS upper 9/15 scoped/source-mapped, new fully complete 0. Original F05 first accepted tick160/131072, proposed tick161 NOT_ACCEPTED. F08 source-owner original science HOLD; F09 provider DOMAIN_BLOCKED. Native subagents absent, native_subagent NOT_RUN. Distinct-author blind referee NOT_RUN, same-author adversarial validation PASS. Production HOLD, NO_MERGE, NO_FORCE_PUSH, NO_ORIGINAL_SOURCE_MUTATION, NO_TOLERANCE_RELAXATION, AUTO_NEXT=false.

Next central task: Transfer this genuine continuous source-energy-tagged photon representation through original REI paired_runtime interval-certified MPRK/SDIRK and all original 14 photon/HHe/thermal ledgers on an immutable owner research branch. More sidecar ray atlases or 1-step conditional snapshots are NOT a central-DAG advancement.

## Immutable source-inclusive preservation
Backup /home/cosmosapjw/archives/BASS_REI_F08_S0_CONTINUOUS_NATIVE_HHE_20261102.zip; bytes=7123265; files=106; SHA256=dc48688e734838a0933fabe97025d7c354ccd972a03ecb8ca6e33be5460e0673. Cold extraction ZIP CRC PASS, exact source SHA51+12+4 PASS, original Rust release compile PASS, 14 normal+14 optimized tests PASS, same-author hostile data audit PASS, actual 160-step four-model 640+320 physical rows and independent prefix64 256+128 physical rows BYTE_EXACT_PASS. Cloud second-provider byte restore is NOT_VERIFIED. This pre-CI ZIP was created before the final GitHub stage B/CI record; final GitHub HEAD is authoritative for published CI contract.
