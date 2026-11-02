# BASS → REI F08 | Source-preserving photon input and original Rust interval root

UNIT=REI_F08_S0_NATIVE_KRAWCZYK_ROOT_CONTINUOUS_SOURCE_20261102.
IMMUTABLE_PARENT_BASS_PR328=b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6.
ORIGINAL_REI_S0_PAIR_SHA256=0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
ORIGINAL_REI_RUST_COUPLED_PRIMARY_SHA256=915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b.
ORIGINAL_REI_ATOMIC_PROVIDER_SHA256=b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3.

## Actual scientific target
BASS PR328 produced 640 continuous actual source S0 photon/HHe/thermal stages from REI original Rust primary_stage_step_conservative, but only point conservation checks. The original REI primary_stage_root forms an interval gas+photon Krawczyk enclosure of a possibly different native point stage. Need check actual self-evolved (not frozen-parent) original S0 gas/photon inputs: can the unchanged original source root enclose the same input's original conservative point output?

Metric (-,+,+,+), a_i=exp(H_i t), H_BI=(1.01,.99,1)e-14 s^-1 or H_FLRW=(1,1,1)e-14 s^-1; proper original S0 dt=625000000 s. Original S0 photons born 13.7 eV, initial N=0.05/H, constant birth 5e-15/H/s on the original 8×16 q directions with original isotropic-source weights. Original gas nH0=1e-4 cm^-3, He/H=.083, initial xHII=.9, xHeII=.3,xHeIII=.6, T=50000K. Keep c=29979245800 cm/s, kB=1.380649e-16 erg/K, original atomic photoionization and chemical binding thresholds separate. Photon true energy E(q,t;t_birth)=13.7 eV sqrt(sum_i q_i² exp(-2H_i t)/sum_i q_i² exp(-2H_i t_birth)). Fixed-hat original conserves photons and first energy moment but violates physical source spectral support.

Original REI interval root uses a four-variable gas y=(xHII,xHeII,xHeIII,w), original photon input. In the exact original code the map G(y)=y-parent_gas-dt*R(y, N_photons(y)), with original thermal/chemical terms and photon absorption. Its Krawczyk test requires q=max row sum |I-C G'(Y)| < 1 and K(Y) strictly inside Y; gas/photons returned as original interval bounds. The root constructs its centre from original primary_stage_step. Original conservative point is primary_stage_step_conservative with StepControl(max_iterations=200,residual_tolerance=1e-15). These are not assumed identical.

This scoped experiment passes exactly point intervals of actual stage input gas and each photon packet through original root. We verify q<1, original native gas point inclusion in interval Y, native photon-survivor inclusion in root photon intervals, finite widths and physical gas domains, for two S0 source backgrounds and two true continuous photon representations at several source proper steps. Any root failure is a real scoped blocker to be recorded, not a PASS. Parent input interval uncertainties (prior birth quadrature, q and H rounding, stage parent root propagation) are NOT yet passed down time. This is point-conditioned local interval-root compatibility only, not a 160-step globally certified IVP.

Actual output: source-locked per-step original packet input snapshots, original Krawczyk root q, gas and photon widths, source characteristic-vs-hat paired gas and photoionization observables. Source owner files remain 51+12+4 byte exact. Local first-step witness returned q≈2.11e-15 (characteristic) and 1.89e-15 (fixed-hat), enclosures containing original conservative gas and photons.

REI central 28/88 reported delta0; Working 33/88 nonadditive; Physical Fast 4/7, BASS upper 9/15 scoped/source-mapped full delta0. F05 original accepted tick160/131072 is NOT the F08 proper step; tick161 unaccepted. F09 provider blocked. F08 original production admission HOLD. NO_MERGE, NO_FORCE_PUSH, NO_TOLERANCE_RELAXATION, NO_ORIGINAL_SOURCE_MUTATION, PRODUCTION_HOLD, AUTO_NEXT=false.

Literature contextual (method, not source identity): Abel, Norman & Madau (1999), ApJ 523 66 DOI 10.1086/307739; Pawlik & Schaye (2011), MNRAS 412 1943 DOI 10.1111/j.1365-2966.2010.18032.x. Original source-owned REI Rust remains authority for exact formulas and certification.
