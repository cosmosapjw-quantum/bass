# REI AX03 independent initial shear and anisotropic stress background supplier

Additive source-frozen Einstein–massless-Vlasov LRS Bianchi-I research lane executed on user's Ubuntu in ChatGPT without separate local Codex. Original REI AX03 cosmology/source SHA 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0, original stress-free q signed family, mean zbar20 to4 and SI proper clock retained.

New independent parameters: q_ref=s_ref/H_FLRW(aref), A from initial positive angular W(mu_ref)=1+A P2(mu_ref) (-1<=A<=2), eta in[0,1] fraction of the EXISTING Omega_r radiation budget. Initial stress DeltaP_ref/epsilon_r_ref=eta*A/5. Stress evolves using exact collisionless Killing phase-space energy/direction, not a fixed invented π(t). Einstein Hamiltonian/shear/energy conservation solved self-consistently for the model. η=0 recovers original AX03.

Files:
- einstein_vlasov_lrs.py: DOP853 and exact directional angular integrals including chunked vector evaluation.
- evidence/AX03_INITIAL_PI_TABLES/AX03_INITIAL_PI_BACKGROUND.csv: 17 cases x501=8517 stress/H/metric/clock/H/He density rows.
- evidence/AX03_INITIAL_PI_TABLES/AX03_INITIAL_PI_KILLING.csv: 8585 exact Killing ray samples with corrected R^-3 Jacobian; companion source SHA/units/assumptions in AX03_INITIAL_PI_CONTRACT.json.
- rust_reference.rs and rust_parity.py: independently coded stdlib Rust Legendre64 RK4 model/8 cases matched to DOP853.
- rust_stress_consumer.rs and test_rust_consumer.py: actual stdlib Rust 8517-row Hamiltonian and stress validation with negative corrupted H/π cases.
- rust_rei_bridge.rs: actual original rei_microphysics BackgroundPoint and GeometrySnapshot compiled using original crate path dependency, all 8517 rows and 5 stress-free source parity.
- xact_stress.wl and evidence/XACT_STRESS.json: 8 exact local symbolic tensor zeros.
- test_einstein_vlasov.py, test_delivery.py, test_evidence.py: 37 new targeted Python PASS; inherited 33 AX03 supplier and 29 C8 shortstep tests PASS.
- benchmark_stress.py: 4096 angular moments 29.22x fully vector, 36.17x chunked with 0.534MB traced temporary peak vs 10.652MB full vector; 2/4 threads slower than serial.
- REPORT_KO.md: complete conventions/equations/derivation/results/positive source assumptions and scientific source limits.

Under BASS worktree run:
python3 -m unittest discover -s research/rei_axbi_anisostress_20261015 -p 'test*.py' -v
python3 research/rei_axbi_anisostress_20261015/rust_parity.py --out /tmp/axbi_pi_rust_8_cases.json
python3 research/rei_axbi_anisostress_20261015/test_rust_consumer.py --out /tmp/axbi_pi_native_validate.json
python3 research/rei_axbi_anisostress_20261015/produce_stress_tables.py --out-dir /tmp/axbi_pi_new_dataset
python3 research/rei_axbi_anisostress_20261015/benchmark_stress.py --output /tmp/axbi_pi_benchmark.json

CAUTION: eta=1 and A=±1 are deliberately extreme initial radiation quadrupoles; no CMB/posteriors/observational acceptance. Original REI AxbiBackground cannot evolve stress-coupled shear and MUST NOT silently consume new pi background as its own source. The bridge only establishes same Rust BackgroundPoint geometry compatibility. A new source-locked η>0 native provider and physical clock/increment + photon collision/chemistry contract must be tested on a new science branch and unique checkpoint source identity. Scientific EoR admission NOT_ISSUED. Real ongoing owner checkout and science jobs not modified.
