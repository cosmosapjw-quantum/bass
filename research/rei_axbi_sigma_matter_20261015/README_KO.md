# AX03 Sigma plus radiation/massive Vlasov initial anisotropic stress

User-defined scalar Sigma_ref=sqrt(sigma_ab sigma^ab/2)/H_ref, with separate shear_orientation (+1 or -1), instead of previous signed q_ref input. Stress normal-frame diagonal tensors pi_r and pi_m are independently controlled by positive initial phase-space angular distributions and existing source energy fractions. **Matter anisotropic stress is real** for massive collisionless matter with velocity dispersion; cold perfect pressureless CDM/baryons in normal rest equilibrium have pi=0.

Implemented and executed on authorized user Ubuntu by ChatGPT; separate local Codex NOT_USED, native subagents NOT_RUN_UNEXPOSED. Parent BASS source commit 68137622de0ab64cee66d9efc13b0a5336a0bd30 radiation Einstein–Vlasov source; original REI AX03 source family SHA 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0. All original BASS kinetic hierarchy sources are SHA-pinned inside sigma_matter.py.

Files:
- sigma_matter.py: actual positive massive Fermi–Dirac original BASS radial quadrature and parent radiation angular Killing moments, Einstein constraint + separate energy conservation + coupled shear, DOP853. Public InitialStress() takes Sigma_ref and signed orientation plus initial radiation/massive quadrupolar source coefficients. InitialStress.from_stress_ratios() accepts physically normalized independently specified initial Pi_r and Pi_m ratios and checks realization.
- evidence/SIGMA_MATTER_TABLES/AX03_SIGMA_MASSIVE_HISTORIES.csv: 14 actual source cases x501 proper-time, geometry, signed s/H, user Sigma, radiation/massive Pi, baryonic H/He nuclear densities. Exact source/user units and SHA manifest in AX03_SIGMA_MATTER_CONTRACT.json.
- test_sigma_matter.py: 23 targeted physical, original BASS J0/J1/J2 and exact source/constraint/realisability tests. Real Rust receiver in rust_rei_matter_bridge.rs builds original unchanged rei_microphysics crate and validates 7014 real rows plus intentional 3 source corruptions. Evidence/NATIVE_REI_BRIDGE.json.
- convergence.py and evidence/CONVERGENCE.json: empirical angular GL16/32/64/128 and tighter DOP853 source-specific comparison; no global interval certification.
- benchmark_massive.py and evidence/MASSIVE_BENCHMARK.json: actual scalar/full vector/chunked/2/4 thread source same-input memory/time comparisons; whole 14 coupled background ODE parallelism measured separately.
- xact_sigma_matter.wl and evidence/XACT_SIGMA_MATTER.json: real local Wolfram Engine 15.0.0 xTensor1.3.0, 10 exact zero tensor residuals.
- plot_sigma.py and evidence/AXBI_*.png: original numerical Sigma and two species stress histories.
- REPORT_KO.md explains source equations, normalization, proven identities, actual empirical results and remaining physical limitations.

Run under this same BASS Git source tree:
python3 -m unittest discover -s research/rei_axbi_sigma_matter_20261015 -p test_sigma_matter.py -v
python3 research/rei_axbi_sigma_matter_20261015/export_sigma_histories.py --out-dir /tmp/SIGMA_MATTER_REPLAY
python3 research/rei_axbi_sigma_matter_20261015/benchmark_massive.py --out /tmp/SIGMA_MATTER_BENCHMARK_REPLAY.json
python3 research/rei_axbi_sigma_matter_20261015/convergence.py --out /tmp/SIGMA_MATTER_CONVERGENCE_REPLAY.json
python3 research/rei_axbi_sigma_matter_20261015/rust_bridge_parity.py --repo /home/cosmosapjw/Dropbox/bianchi/rei_bianchi --target /tmp/SIGMA_MATTER_CARGO --out /tmp/SIGMA_MATTER_REI_NATIVE_REPLAY.json

Native REI integration is a typed independent SOURCE interface, not a production Rust coupled physics or full chemical solver replacement; do not resume original AX08 checkpoints under changed pi-source physics. The BASS frozen massless radiation and massive hierarchy are distinct from REI PR133 illustrative viscosity and PR135 cold free streaming. Full HII/He and ionizing source admission NOT_ISSUED.
