# Physical REI background supplier: independent initial Sigma and kinetic Pi(gamma,nu,massive)

Continuation of original BASS PR160 and REI PR137. Implemented and actually executed in this ChatGPT thread using the authorized Ubuntu workstation. No local Codex. Native subagent creation not available. All original repository source and the original AX08 native chemistry owner checkout remain unmodified.

This research implements one physically constrained nontilted axisymmetric Einstein/Boltzmann/Vlasov **background**: initial Sigma=sqrt3|s|/H (signed orientation separately), independent initial positive photon, collisionless massless neutrino and original BASS FD96 massive matter P2 quadrupoles. The massive source takes a fraction out of original Omega_m (nonbaryonic cap) with the remainder cold dust, eliminating double count. Photons gamma only have source-real original AX08 q0 electron donor for elastic unpolarized Thomson; neutrinos never Thomson scatter. New background does not feed back its chemistry into n_e or ionizing source.

Pinned original source topology:
- BASS PR160 parent 9e50f936f3289cb0c7c8127772cf9fb8d172d7a8, original BASS FD96 and radiation Einstein f0 sources.
- REI PR137 parent 5d41df647c4fd624d8a1b574f67fdd0b82ff5102, exact-byte copies in source_refs/ and source SHA pins in joint_kinetic.py.
- Original AX03 frozen BACKGROUND_FAMILY_LOCK sha256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0.
- Real AX08 q0 history sha256 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f verified before one-way donor read. The 159MB original HHe source history is **not** published or copied into the source archive.

Actual files:
- joint_kinetic.py: direct Einstein/H/shear source and real unpolarized photon/nu hierarchy with BASS massive kinetic stress; separate donor input.
- run_joint.py: actual eight scenario, 401-node each source histories, 3208-row typed CSV and machine-readable case/physics receipts in evidence/JOINT_CAMPAIGN/.
- validate_joint.py: exact parent BASS massive/REI gamma-nu limiting parity and finite L/massive angular/ODE refinement.
- native_bridge.py + rust_rei_joint.rs: compiles true original rei_microphysics::BackgroundPoint via external Cargo target, checks all 3208 rows and four purposefully corrupted source rejections. The source is **not automatically adopted by native REI chemistry**.
- benchmark_joint.py: real 12-case DOP853 1/2/4 PROCESS workloads, BASS FD96 1024 moment sample scalar/unbounded/chunk64/128 memory and timing.
- test_joint_kinetic.py (20 science regressions) and test_evidence.py (15 actual source/evidence regressions). Parent original BASS PR160 test_sigma_matter.py 23 tests also pass.
- xact_joint.wl and evidence/XACT_JOINT.json: actual local Wolfram15.0.0/xTensor1.3.0 8 zero tensor conventions.
- REPORT_KO.md: theorem-to-code normalization, exact derivation, data and numerical claim limits.

Some actual endpoint Sigma for Sigma_ref=0, k_gamma=k_nu=.2, f_m=.1, A_m=.5, mass/Tref=30:
 radiation only0.000102070322; massive only0.0000287960934; both0.000130902704; both plus original AX08 one-way Thomson0.000130324057. Physical independent full original BASS Einstein massive and radiation exact source limit holds to <5e-13 for signed legacy q=0,+.01,-.01. Photon/masslessnu zero-mass limit is bitwise RHS-compatible and state difference <4e-15 at identical DOP853 tolerances. Actual original REI-native Rust intake all3208 row Hamiltonian max relative residual3.33e-16, Sigma 0 error, four negative tests rejected exit3. This is kinetic BACKGROUND physics only, not full native coupled stellar reionization or observational inference.

Local performance: 12 independent DOP853 physical cases serial0.6644s, 2 Python fork processes0.4707s, 4 fork processes0.2917s, exact endpoint equality. Original BASS massive FD96 1024 evals scalar0.0736s; chunk1280.0193s traced12.8MB vs full NumPy0.0987s traced101.6MB, chunk64 trace6.47MB. These are actual one-workstation empirical source component times, not a whole native HHe speedup.

Run under exact BASS checked-out tree:
  python3 -m unittest discover -s research/rei_sigma_kinetic_gamma_nu_20261015 -p 'test_joint_kinetic.py' -v
  python3 -m unittest discover -s research/rei_sigma_kinetic_gamma_nu_20261015 -p 'test_evidence.py' -v
  python3 research/rei_sigma_kinetic_gamma_nu_20261015/validate_joint.py --out /tmp/rei_joint_refinement.json
  python3 research/rei_sigma_kinetic_gamma_nu_20261015/run_joint.py --out /tmp/rei_joint_new_campaign   # needs original REI AX08 source history
  python3 research/rei_sigma_kinetic_gamma_nu_20261015/native_bridge.py --repo /path/to/actual/rei_bianchi --target /tmp/rei_joint_cargo --out /tmp/rei_joint_native.json

Only the new additive native table intake is proposed for REI. No original AX08 checkpoint may be resumed under a different Einstein background/physical radiation source identity. Scientific status remains NOT_ISSUED for full HHe background coupling, polarized Thomson, calibrated massive source and AX11 errors.
