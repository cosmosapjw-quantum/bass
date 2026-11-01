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
## C7. 물리·관측량 검증

The two original rays preserve n=±e_y with zero direction defect. Their normal energy final ratios agree at 0.7806210628345815; electron-rest energies differ at 0.7449536005398912 (+) versus 0.8179962393622404 (-). Unit electron-rest optical depths are 0.19055295929452346 versus 0.2099155839589957, giving asymmetry 0.048349926581410956. This is source-conditional physically meaningful mathematical data, not observational cosmology.
## C8. 독립 수치 정확도

8-point and 16-point Gauss-Legendre endpoint opacity integrals agree with independent adaptive quad within 1.2e-16; 1-point midpoint error is ~1e-11, 2-point already at binary64 floor on this smooth 400-interval source. Exact piecewise Hermite integral of Sigma22 equals the direct adaptive quad at the printed binary64 output (0.047665441721635005). This is a tightly scoped convergent quadrature result and does not certify a generic full-angle Boltzmann solver.
## C9. 적대적 검토 및 실패 분류

Self-adversarial checks require an explicit failure if symmetry assumptions are relaxed: Sigma_xy=0.02 yields n_x'=-0.02. Missing Gamma changes T+ by 2.22936e-4, and extra q changes T+ by 9.21304e-3 on the source fixture. Invariance of axial rays CANNOT detect wrong Bianchi curvature sign; off-axis parent validation is necessary. No native subagent or distinct-author independent review ran. The only repair here replaced bypassable Python asserts with explicit exceptions and verified normal/-O parity; no source physics changed.
## C10. 게시 판정·후속 실행

Exact source-conditioned axial oracle dataset and reproducible code are ready for source-scoped research reuse, not for production, fitting or CMB. Preserve `THEORY.md`, `CODING.md`, `AXIAL_ORACLE_RESULT.json`, `AXIAL_ORACLE_401.csv`, `AXIAL_ACCURACY_RESULT.json`, `test_axial_negative.py`, and the copyable `NEXT_THREAD_HANDOFF.txt`. All R1–R10/C1–C10 stage receipts are in an owner-host backup log and distinct Git commits, scoped DAG baseline 9/15 unchanged, new full upper nodes 0. Positive next action: obtain physical electron density/ionization source and couple the actual Thomson kernel to Liouville plus angular remap, while preserving parent/legacy evidence.
