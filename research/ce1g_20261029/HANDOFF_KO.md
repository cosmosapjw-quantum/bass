# BASS CE1-G 다음 연구 스레드 인계 · 2026-10-29

$physmath-research-loop $scispace $exa $wolfram

```
PROJECT=BASS
REPO=cosmosapjw-quantum/bass
PARENT_PR=239
PARENT_SHA=9de0f37955f259b5e9172ce406d1353bf7cc3695
CURRENT_PR=240
CURRENT_BRANCH=research/bass-ce1g-tabulated-wholepath-20261029
CURRENT_HEAD=CHECK_REMOTE_AT_RESUME
UNIT=CE1-G_SCOPED_MPFR_TABULATED_WHOLE_PANEL_SOURCE_TIME
R_C_STAGE_OUTPUTS=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
UPPER_DAG=9/15
UPPER_CE1=PARTIAL
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false
```

## 확인된 연구 결과

- Positive piecewise-constant first-octant angular-energy cells reflected into eight octants; diagonal collisionless massless Bianchi I, Lambda0, normal time `u=t/Tstar`, metric signature(-,+,+,+).
- Same exact-binary physical table and shear as parent CE1-F. `u=0..0.08`, four RK4 panels, exact-real binary Hermite polynomial and exact-real stored ray/mass source.
- CE1-F MPFR source+initial mismatch combined with CE1-C Taylor3/analytic4 whole-panel residual and **explicit exact-binary Hermite endpoint jump correction**. The latter is required because rounded Hermite coefficients do not necessarily meet the next stored knot in exact-real arithmetic.
- `refinement16` (1536 rays): source h upper `2.8664006500876736e-6`; time+jumps `8.35515799694146e-7`; total `3.7019164499698285e-6`, below fixed `1e-5` target. Refinements1/2/4/8 do not meet target; do not suppress failures.
- Independent GL40 original-cell DOP853 gap `6.543159869476511e-8`, a falsification check only.
- `72` scoped local tests PASS, GitHub Actions run `40790375589` job `123173834020` SUCCESS, log `72 passed in 14.65s`, installed-wheel smoke PASS.
- Wolfram and SymPy fourth-derivative coefficient residuals both zero; no formally machine-verified Python/MPFR or independent authored full science review.

## GitHub and provenance

- Draft PR: https://github.com/cosmosapjw-quantum/bass/pull/240
- Exact source Git blob: `8daa44d413aca912edb0918d31caad6182ad2bd3` for `bianchi/nonperturbative/einstein_tabulated_time.py`.
- Exact test Git blob: `b5eacd9ca23e0050a49a8774d39c0f2561f25d5e` for `tests/nonperturbative/test_einstein_tabulated_time.py`.
- Theory Git blob: `d3006bb7e29b290dad259b9c3b8059b81f1457ab`.
- Workflow Git blob: `4ebb23abfaddc9d61adbe451f62d907051d990e2` after push-only and concurrency policy repair.
- 20 stage notes each posted in Git with exact readback, 20 immutable local stage ZIPs, 20 actual Google Drive uploads with matching size metadata. C10 original Drive ZIP has whole-file SHA256 `fc2916c0f4a35d642056e47c93d2e393c8402f0f9c841a2b31655b6d1dc056b2` and full byte readback PASS.
- Dropbox ZIP upload NOT_DONE: Library Dropbox mount read-only and generated-file `source_file` adapter not available. Do not assert Google Drive+Dropbox dual backup.
- Source archive and final SHA/Drive ACK are recorded separately in FINAL_DELIVERY_ACK.json if uploaded. Preserve the source ZIP without regenerating it to insert post-archive receipts.

## Reproduce locally

1. Re-probe runtime. Never inherit previous runtime availability claims. Pin source to PR240 actual HEAD and verify source/test blob identity.
2. Read `research/ce1g_20261029/THEORY_KO.md`, `REPORT_KO.md`, `DAG_UPDATED.json`, `STAGE_LEDGER.json`, `evidence/SCIENCE_RESULTS.json` and original parent CE1-F ZIP.
3. Targeted test: `OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/nonperturbative/test_einstein_tabulated_time.py tests/nonperturbative/test_einstein_tabulated_source.py tests/nonperturbative/test_einstein_exponential_source.py tests/nonperturbative/test_einstein_physical_input.py tests/nonperturbative/test_einstein_interval.py tests/nonperturbative/test_einstein_error_budget.py`.
4. Saved evidence readback is preferred. Re-run expensive science only if changing code/input/contract or an independent reviewer needs it: `OPENBLAS_NUM_THREADS=1 PYTHONPATH=. python research/ce1g_20261029/evidence/run_science.py`.
5. Distinct-author R6/C9 independent review must challenge `_p4_interval` majorant for generic positive stored rays, exact binary knot jumps, CE1-F pressure-box source enclosure, Emax choice, and entire expanding-octant domain. CAS or same-author alternate algorithm is not an independent author.
6. Do not merge PR238 and PR239/240 blindly. PR238's previously reported Emax issue must be independently reconciled; no cross-repo source/rate activation.

## Next science candidate, not executed

CE1-H: rigorous implementation-level assurance of MPFR bindings and initial physical input acquisition for the selected CE1-G table, or independent validation of a **separate** collisional/polarized channel after electron-frame collision source contracts are frozen. Prioritize an independent exact interval backend/third-party review before generalizing geometry families. Preserve original 15 DAG nodes and 21 edges; current upper 9/15, CE-1 PARTIAL. No automatic next node, no production/native admission or merge.
