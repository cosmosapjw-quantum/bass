# REI AX03 source-frozen independent initial anisotropic stress background

Actual construction and execution: source-matched Bianchi-I Einstein–Vlasov, initial shear q_ref in {0,+/-.005,+/-.01} plus independent positive quadrupole kappa in [-.5,.5]. Original background Cosmology/Omega/H0/mean redshift interval/clock are kept exactly by source-lock SHA256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.

This is a NEW conditional collisionless cosmic radiation lane, not an old AX08 stress-free native driver replacement or an ionizing CMB/Thomson coupled solver. Any REI scientific observation and H/He abundance admission remains separate.

Source:
- einstein_vlasov.py: DOP853 coupled Einstein shear and radiation energy, exact angular Killing moments W=1+kappa P2, M_b=-6P, physical density SI.
- vector_batch.py: source-matched 10-case vector RK4 optimization, measured speed and accuracy.
- export_histories.py: typed SI energy/stress and 5010-row 10-case background CSV.
- mp_moments.py: actual independent mpmath75 angular moment checks.
- parallel_bench.py: real 1/2/4-thread benchmark, slower than vectorization.
- test_einstein_vlasov.py: 18 physical regression tests.
- xact_stress.wl: native Wolfram/xTensor8 zero tensor groups.
- plot_stress.py: the four actual scientific curves.
- evidence/TABLES/AXBI_INITIAL_STRESS_BACKGROUND.csv + manifest SHA.
- REPORT_KO.md: equations, units, assumptions, tested scope and future native intake gates.

Use from BASS root:
python3 -m unittest discover -s research/rei_axbi_initial_stress_20261015 -p test_einstein_vlasov.py -v
python3 research/rei_axbi_initial_stress_20261015/einstein_vlasov.py --output /tmp/pi_new_pilot.json
python3 research/rei_axbi_initial_stress_20261015/mp_moments.py --out /tmp/pi_new_mp.json
python3 research/rei_axbi_initial_stress_20261015/export_histories.py --directory /tmp/pi_new_tables

Native Rust rei_microphysics::axbi_stress_background is an opt-in production-crate module on the isolated REI research branch; no original axbi_driver callsite uses it. Native tests in tests/axbi_initial_stress.rs check physical kinetics, constraints and 10 endpoint Python parity. No local Codex used. REI original owner branch and full science processes untouched.
