# CE1-P S1 | Native BASS Rust core used in real current-head GitHub CI

**Parent** PR256 HEAD `3a7a38f9615f100fddda0379bd3d6ec359ccc586`; **child** Draft PR257, no parent/main writes. Upper DAG **9/15**, 21 edges, CE1 PARTIAL.

**Actual compiler/rust source:** Rust 1.94.1 via GitHub Actions [40884723128](https://github.com/cosmosapjw-quantum/bass/actions/runs/40884723128) SUCCESS. Workflow SHA-pins `_rustcore/src/kinetic/comoving.rs` at Git blob `a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84`, and compiles live native BASS `Frame::apply/det/step`, **not the historical offline module**. Rust source diagnostic `research/ce1p_20261029/rust_comoving_stress.rs` Git blob `2726a1336a6584f3820289a9ea47f1beca3295dc` and Python independent comparator `compare_rust_to_ce1.py` blob `cff82535d13be36258b3843340989120d0a531ea` exact local tested bytes.

**Science:** use `M=diag(e^-ell)`, `E_Q=det(M)sum w|Mn|`, `P_Qi=det(M)sum w(Mn)_i²/|Mn|`, `J_ij=-(1+2delta_ij)P_i+det(M)sum w(Mn)_i²(Mn)_j²/|Mn|³`. Validate massless trace `sum_i P_i=E`, row-sum `sum_j J_ij=-4P_i`, common-shift pressure `e^-4s`. Native `Frame::step` is e-fold `tau`, **not** CE1 proper `u=t/Tstar`. All binary64 native results are *diagnostic*, **not** MPFR192 directed proof.

**Observed current-turn facts:** local isolated Rust native selftest 4 PASS; Python differential across positive stored source refinements 1/2/4/8 (6/24/96/384 rays), 24 source settings, 96 states and legal current-ray/mass variations; original ref8 source SHA exact match historic CE1-M. Maximum absolute gaps (Rust/Python) E `3.219646771412954e-15`, P `1.6653345369377348e-16`, Jacobian `5.551115123125783e-16`; massless trace `3.9968028886505635e-15`, Jacobian row sum `6.661338147750939e-16`. Four invalid current-source cases rejected.

**Actual GitHub CI log [run 40884723128](https://github.com/cosmosapjw-quantum/bass/actions/runs/40884723128):** `rustc 1.94.1`, `CE1P_RUST_SELFTEST_4_PASS`, `CE1P_NATIVE_REJECTS_BAD_RAYS_4_PASS`, `CE1P_RUST_BASS_COMOVING_STRESS_AND_JACOBIAN_DIFF_PASS`; **83 passed in 18.03s** inherited CE1 source/program regressions. This CI compiles *the exact current-head BASS rust source*, closing the S0 historical module-byte limitation.

**S0 immutable backup:** ZIP 9,765 bytes SHA256 `a5e754d2d941835054d43ba6aee41a8823dc7c0b85a202c32d7f1cfd6c5a0e4d`; Google Drive file `12G8DS2mwtACeR9g4m7B3i9hBbtxuPGVb` full byte readback MATCH; Git S0 `8b74a37368688ac56ba3964433140d309e00feab`. **Dropbox ZIP upload blocked**: library provider read-only; connector fileParams wrapper rejects correctly sourced file objects/IDs. Do not claim Dropbox success.

**S1 immutable backup:** `BASS_CE1P_S1_20261029.zip`, 18,948 bytes, 8 members, SHA256 `4a6007d5665178f867f274639f606ba7ddf6b66c61075598e4e7d144fd5fe1b0`, ZIP CRC+manifest PASS; provider upload and readback to verify after posting.

**Admission:** CE1 parent results preserved; no new upper-level completed node, **9/15**. `production_ready=false`, `merge_ready=false`, `auto_next=false`; no full MPFR/GMP program proof or distinct-author external review. Next S2: final machine-readable science and delivery report + reusable handoff; no automatic merge.
