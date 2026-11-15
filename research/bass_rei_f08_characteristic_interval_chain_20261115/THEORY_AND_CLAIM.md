# BASS F08 original birth-characteristic gas/photon interval chain, 2026-11-15

**Physics target:** Original REI F08 S0 constant-diagonal-Hubble Bianchi-I and matched FLRW IGM, with *actual original* photoionization H/He and gas thermal native Rust operators. Preserve exact original 13.7-eV birth source, 128 8x16 q directions, birth time, original angular photon source Jacobian and 625000000-s proper stage clock. No reinterpretation of F05 tick, 14-ledger owner admission or production.

**Immutable upstream:** BASS PR331 f61dcb4314eed3897106c0e6177f043c770325de; PR328 b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6; original S0 source pair 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8; original REI Rust coupled_primary.rs 915d0a898100a54d04a525227e7fbeb870e321fcc14aaa91afd61352b6d4cf4b; paired_runtime.rs b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7.

## Constructive R5 theorem: physical photon support

For a diagonal Bianchi-I metric ds²=-c²dt²+Σa_i²(t)(dx^i)² and constant H_i≥0, canonical momentum direction q, and physical photon energy E_b at emission time t_b, the null Liouville redshift law is

 E(q,t;t_b)=E_b [Σ q_i² exp(-2H_i t)/Σ q_i² exp(-2H_i t_b)]^(1/2).

Differentiating the logarithm gives d(log E)/dt=-Σ_i H_i w_i(t), where w_i=q_i² exp(-2H_i t)/Σ_j q_j² exp(-2H_j t), w_i≥0, Σ w_i=1. Thus for every birth event t_b≤t,

 E_b exp[-H_max(t-t_b)] ≤ E(q,t;t_b) ≤ E_b exp[-H_min(t-t_b)].

Original interval arithmetic computes the outer endpoints for the original binary64 H and elapsed proper time; the actual source energy is 13.7 binary64 eV. Every tracked survivor is required to lie in this bound, and its point energy must remain above the global source floor E_b exp(-H_max t). Absorption destroys packets but never remaps their energy to a forbidden node. This avoids PR331 fixed-hat support leakage.

## Native finite chained construction and exact claim ceiling

In BASS-only additive Rust example bass_f08_characteristic_interval_root.rs:
- A PrimaryBox contains the **previous returned original gas root interval** in (x_HII,x_HeII,x_HeIII,w), and previous returned original photon survivor-number intervals, plus the current emitted positive-number boxes enclosing actual original source f64 emission quantities.
- Each packet retains its original angular index, birth time, and f64 exact-characteristic energy, and a separately computed original Rust Interval analytic Hmin/Hmax energy enclosure.
- Calls the original immutable primary_stage_step_conservative and primary_stage_root, with the original StepControl(max_iterations=200,residual_tolerance=1e-15).
- Only the BASS wrapper links original continuous source packets by time and q to the native original gas root; previous box enclosures are passed forward consecutively with no resets.
- Original photo event and gas/energy point ledgers are recomputed; per-packet photon and gas root box containment and q<1 checked; original no-tolerance-relaxation maintained.

**Limited result:** This is a real *finite F08 source-conditioned* original Rust gas-and-photon-N interval chain with actual original f64 characteristic packet energy at each stage. It proves **neither** enclosure of the non-point energy-dependent photoabsorption cross section in the original gas root, **nor** q/birth time uncertainties as gas input parameters, nor a continuum ODE global-error theorem, nor the REI owner 14 interval ledgers. Analytic energy bounds do not repair the unchanged root's point-energy parameter interface. Source angular weights are fixed original binary64 values; the emission count boxes enclose that binary64 center by outward ULPs, not proven all uncertainties in source angular quadrature. Temperature/escape work interval ledger remains absent. This explicitly forbids falsely promoting a point-energy interval root to a global photon/gas solver.

**Drift watchdog:** new physical data must actually yield H/He/T/N under characteristic support-preserving photons and propagate parent gas/photons enclosures through consecutive native stages. Unrelated Type-II source atlases, tolerance changes and ornamental meta-controls contribute zero. A failed original root must be recorded as an actual current blocker, not silently replaced with point parents.

**Reference methods, not assumed equivalence:** Abel, Norman, Madau 1999, ApJ 523 66, DOI 10.1086/307739; Pawlik & Schaye 2011 MNRAS 412 1943 DOI 10.1111/j.1365-2966.2010.18032.x; Leong et al. 2023 MNRAS DOI 10.1093/mnras/stac3828. Native REI source remains exact physics authority.

**DAG:** Central REI 28/88 reported; working 33/88 nonadditive; Physical Fast 4/7 reported; BASS upper 9/15 scoped; canonical delta=0; F08 owner HOLD; original F05 tick160/131072, tick161 not officially accepted, F09 blocked; production HOLD.
