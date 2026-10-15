# REI AX03 source-locked Bianchi I background supplier

This is a genuine new BASS-to-REI background supply lane. It is not an automatic continuation of previous FA03 C10 and does not replace the original rei_bianchi native Rust background. ChatGPT authored and actually executed source-matched background calculations in the user's Ubuntu 24.04, WITHOUT local Codex. Native subagent NOT_RUN (not exposed).

The actual original AX03 background lock is byte-identical in source/REI_BACKGROUND_FAMILY_LOCK.json. Model: physical-density-fixed stress-free non-tilted LRS Bianchi I in signature(-,+,+,+), mean a=1/21->1/5, five physical q_ref=0,+/-.005,+/-.01 plus separately labelled SAME_H +.01 diagnostic. Proper time is SI elapsed seconds from mean redshift20. The exact axes are a_perp=a exp(-b), a_parallel=a exp(2b), Hperp=H-s, Hpar=H+2s and Sigma=s/H. All mean H and baryon nuclei density inputs are source-pinned. The photon Killing momentum map gives exact real source-free anisotropic photon energy/direction and phase-volume Jacobian, independent of toy FA03 opacity.

**Actual supplied data**:
- evidence/AX03_SUPPLIER_TABLES/AX03_BACKGROUND.csv: 3006 points over six real/diagnostic scenarios, field units/columns in AX03_SUPPLIER_CONTRACT.json.
- evidence/AX03_SUPPLIER_TABLES/AX03_PHOTON_KILLING.csv: 7530 forward/earlier photon sampled mappings for five face mu values and all six scenarios.
- evidence/MP_ORACLE_INITIAL.json: 70dps independent mpmath reference integrals on 30 points, max proper-time relative difference8.35e-13 and b absolute2.20e-16.
- evidence/RUST_PARITY_INITIAL.json: actual original Rust AxbiBackground compiled and executed on those 30 matched points, source SHA pins and max time relative1.25e-12.
- evidence/IGM_RUST_PARITY.json: actual original Rust FlatFlrwBackground H/nH/nHe/Tbar/clock 11-point input parity, worst relative4.44e-16.
- evidence/BACKGROUND_BENCHMARK.json: source-matched direct Rust Simpson4096 vs Python DOP853 preintegrated vector batch at 6x501 scales, query-only speed107.65x; NOT full REI speedup or over original Rust cached table.
- evidence/NATIVE_TABLE_NEGATIVE.json: native Rust stdlib CSV consumer full PASS, H_mean changed +5% negative test exit3, original CSV SHA intact.
- evidence/FEEDBACK_PROXY.json: numerical effective Omega_r free-streaming stress proxy, small |delta_s/H| around1e-5 for |q|=.01 but ~0.87% relative change of original shear at z4; NOT a rigorous bound on unknown ionizing radiation stress or actual CMB histories.
- Three plotted curves of signed b(zbar), H/HF-1 and proper elapsed time.

**Commands under BASS worktree**:
python3 research/rei_axbi_background_supplier_20261015/axbi_provider.py
python3 research/rei_axbi_background_supplier_20261015/produce_tables.py --output-dir /tmp/axbi_supplier_new
python3 research/rei_axbi_background_supplier_20261015/mp_oracle.py --output /tmp/axbi_mp_new.json
python3 research/rei_axbi_background_supplier_20261015/rust_parity.py --rei-repo /path/to/rei_bianchi --target-dir /tmp/axbi_rust_build --output /tmp/axbi_rust_parity_new.json
python3 research/rei_axbi_background_supplier_20261015/igm_parity.py --rei-repo /path/to/rei_bianchi --target-dir /tmp/axbi_rust_build --output /tmp/axbi_native_igm_new.json
python3 research/rei_axbi_background_supplier_20261015/benchmark_background.py --rei-repo /path/to/rei_bianchi --build-target /tmp/axbi_rust_build --output /tmp/axbi_host_benchmark_new.json
python3 research/rei_axbi_background_supplier_20261015/validate_native_tables.py --output /tmp/axbi_native_consumer_new.json
python3 -m unittest discover -s research/rei_axbi_background_supplier_20261015 -p test_axbi_supplier.py -v

Native Rust original-source parity needs an accessible original REI checkout with exact source SHA, and uses external Cargo target. For a fresh unrelated machine without the checkout the public CSV and the independent Python solver are standalone. Do not treat old source/Git HEAD as automatically current.

Important distinction: Tbar_CMB_K is isotropic reference T0/a, not actual direction-dependent CMB temperature. Source-free photons obey (Ei/Ef)^3(dOmega_i/dOmega_f)=(af/ai)^3, but real ionizing absorption and feedback require actual physical radiation and gas solutions. Use strict source tables as external REI scientific inputs only after own source clock and short-interval interpolation verification. No q-dependence may be post-hoc fitted from observed chemistry.
