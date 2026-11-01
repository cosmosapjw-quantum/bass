# Original BASS Type-II axial ray exact physical research

## C1. 실행 대상과 품질 기준

Implement a reproducible source-locked exact axial oracle and compare 401 published source-conditioned records for both e_y directions. Acceptance: all original 9 Git blobs and parent CSV SHA locked; no mutation of original source; normal and optimized Python checks; exact direction, redshift, electron Doppler, optical-depth parity and negative controls. BASS production gates remain HOLD.
## C2. 수식-코드-데이터 매핑

`verify_axial_analytic.py` reads original `compiler/validation/typeii_fixture_canonical.json`, its `samples[*].state` and `samples[*].rhs`, plus immutable parent `PHOTON_RAYS_401X26.csv`. It chooses ±ey by measured initial ray vectors, not by assuming list index, then compares normal and electron frame energies plus optical depth at every 401 time sample. `test_axial_negative.py` is a separate narrow counterexample suite and `verify_axial_accuracy.py` checks numerical quadrature.
## C3. 독립 계산 형식

For the source Hermite interpolant of Sigma_++√3Sigma_-, integrate each interval exactly as h(f0+f1)/2+h²(f0'−f1')/12. Integrate the nonlinear Gamma(1∓v2) with 8-point positive Gauss-Legendre on 400 intervals and independently with adaptive `quad`. Construct both optical depths from integrated Gamma and Gamma*v to retain the odd/even analytic identity. No new dynamic photon solver or production runtime changes.
## C4. 자원·실행·체크포인트

Use the authorized isolated local Git worktree `research/bass-typeii-axial-ray-exact-20261102-r1`, ordinary Python+SciPy and OpenBLAS=1. Prior 401x26 parent photon data is read-only. Stage commits/pushes must be remote SHA-read back and copied to local ZIP archives with SHA-256 and `unzip -tq`; no GPU, no extra service provisioning, and no edits to `/home/cosmosapjw/bass` current owner branch.
## C5. 실제 코드·물리 산출물

`verify_axial_analytic.py` creates 401-row exact-oracle CSV/JSON, enforces original nine Git blob identities and parent ray byte identity, selects ±ey by initial physical directions, and compares all 401 original ray outputs. `test_axial_negative.py` and `verify_axial_accuracy.py` are executable auxiliary validators. In this cycle the physical scripts and input-conditioned data were already created and run before the formal stage record; this stage reuses that actual verified implementation, not a simulated run.
## C6. 코드 실행·회귀

All three Python scripts parsed as AST and executed normally and under python -O after converting 22 critical Python asserts to explicit raise-on-failure gates, preventing optimized mode from silently skipping numerical validation. Original input source checksum and parent CSV SHA remained unchanged. The axis exact oracle printed its per-field residuals and adaptive quadrature check with actual exit 0; production crate tests are inherited from PR #325, not rerun or attributed to this branch.
