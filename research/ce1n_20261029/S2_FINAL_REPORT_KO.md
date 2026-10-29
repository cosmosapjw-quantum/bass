# CE1-N S2: exact-current-source MPFR directed program assurance

**Parent:** Draft PR252 HEAD `8e26188d03197b0a4f878c5ce98e015468a4e24b`; **current:** Draft PR254. Protected: same positive massless collisionless expanding diagonal Bianchi I, Lambda0, metric(-,+,+,+), u=t/Tstar, h=Tstar H, original 6-cell/angular source, 4 RK4/Hermite panels, MPFR192 and original fixed target `max|delta h|<1e-5`. Upper DAG **9/15**, CE-1 PARTIAL.

## P1 failures and exact minimal repairs

1. `_mismatch_coefficients(source,K)` used K-only unkeyed exact-rational polynomial mismatch cache across positive current ray/mass input rebinding. At ell0, original pressure x cap `1.193178730416563e-15` was reused after mass×2, despite exact continuum pressure x `0.294` and MPFR-valid current discrepancy lower `0.29399999999999954`. Positive current ray factor1.001 gives gap lower `0.0002939999999997139` vs old stale bound `2.586594364224074e-12`. **Repair:** recompute exact mismatch from present binary source per call; no K-only cache. Polynomial quadrature physics and MPFR remainder unchanged.
2. `residual_taylor_mpfr(...,subcells=-1)` skipped verification and returned `ell_defect=h_defect=0`, whereas valid count1 gave ell `2.031227104497378e-5`, h `0.00010464230321653613`. **Repair:** reject bool/non-int/out-of-range counts outside 1..256 before heavy MPFR operations. The high-level CE1G time API already had separate 1..32 validation.

**Verified code Git blob:** interval module `e3a5b83183bfad45bbf38c3c3de89de72fe3adce` (parent `abbab0990fdefaf535ccbf5191ae3e060cb19214`). New regression test Git blob `e368508f3f0c27ecd990272fd63266206406e163`.

## Executed evidence

- Original targeted RED `3 failed / exit1`; local new+inherited MPFR green `24 passed in 5.96s / exit0`.
- Exact Fraction arithmetic oracle **200×4=800** includes; independent 100dps mpmath elementary exp/sqrt/sinh/cosh/tanh **60×5=300** includes, all PASS in current runtime. This tests observed outputs, not a formal proof of CPython/MPFR binaries.
- Original positive source bound remains exactly `[1.193178730416563e-15,9.203870421087771e-16,5.770042555878051e-15]` with valid input. After positive mass×2 current-source bound `[1.763999999999998,1.4039999999999986,2.2320000000000113]` encloses true exact discrepancy lower `[0.29399999999999954,0.23399999999999968,0.3720000000000019]`.
- Adversarial independent positive-current-source mutation sweep: 36 deterministic mass/ray factors ×3 directions = **108 exact rational/MPFR comparisons**; 0 undercoverage, maximum `gap_lower / declared_upper = 0.25359914030698755`. Full script `STRESS_CURRENT_SOURCE.py`, log and inspected figure in final ZIP. A sample is not global formal machine verification.
- GitHub Actions scoped [#40872488061](https://github.com/cosmosapjw-quantum/bass/actions/runs/40872488061) at code HEAD `fcdd9be50d146d0899f9dd56d33e5410b07b4aad`: **138 passed in 18.84s**, original CE1-M ref8 `9.411551484445186e-6 < 1e-5` scientific replay, and installed wheel fail-closed direct MPFR test PASS. Original CE1C MPFR #40872488096 SUCCESS, RF-BENCH #40872488183 SUCCESS. A dedicated S2 CI step adds the 36-source stress; read LIVE final-head run conclusion before promotion.

**Bounds of claim:** source current-input and direct-time partition program proof premises repaired, not a formally verified MPFR/ctypes/CPython implementation; no native Rust production, polarized/tilted/inhomogeneous solver or distinct human-author R6/C9 claim. `production_ready=false`, `merge_ready=false`, `auto_next=false`; no parent/main merge. Upper DAG **9/15**, original 21 edges.

**Checkpoint:** create-only S0 `BASS_CE1N_S0_20261029.zip` SHA256 `b24a52e1bc44c360ff35902ab98cc8003ae7af37af826bfa903c363335dee538`; S1 `BASS_CE1N_S1_20261029.zip` SHA256 `f9cd5c21fe931cc54bdfcb2d7dbbec6a0ebe29a61cdb3866cca326897756f60c`; S2 full `BASS_CE1N_S2_FINAL_20261029.zip`, **124180 bytes, 15 entries**, SHA256 `cb4451bc80fa09af8a7e8ece6f7bf222afebc0c51572f6f96a2dbf7422dcd15d`, manifest 14/14 and CRC PASS. Each provider receipt is in `DELIVERY_RECEIPTS.json` once uploaded. S2 ZIP contains complete Korean report, handoff, source, tests, RED/GREEN logs, stress script/data/figure and nested S0/S1 archives.

**Next research unit:** actual independent-author R6/C9 or formal MPFR ctypes C ABI + correct rounding program-level audit. Preserve frozen past valid ref8 result and provenance; do not add new top-level DAG node until real gate evidence.