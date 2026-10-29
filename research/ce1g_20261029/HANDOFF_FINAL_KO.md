# BASS CE1-G 최종 복사 인계

$physmath-research-loop $scispace $exa $wolfram

PROJECT=BASS
REPO=cosmosapjw-quantum/bass
PARENT_PR=239
PARENT_SHA=9de0f37955f259b5e9172ce406d1353bf7cc3695
CURRENT_PR=240
BRANCH=research/bass-ce1g-tabulated-wholepath-20261029
HEAD=READ_CURRENT_REMOTE_ON_RESUME
UPPER_DAG=9/15
CE1=PARTIAL
STAGE_OUTPUTS=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false

## Source and immutable backup

Original source ZIP BASS_CE1G_FINAL_20261029.zip, 15527023 bytes, 85 members, SHA256 8657f6e7ad51b516896c0a9988644b12790b6cdc48372e14945f8232c4942448. Original includes CE1-F 14.5MB parent archive, 20 stage ZIPs, code/test/workflow, all saved science/plot and full machine-readable contracts. Drive https://drive.google.com/file/d/11IDvF0TFV-f1lDd98kzb0wk_lb5w4ed9/view original FULL_BYTE_READBACK_MATCH and 84/84 payload SHA/CRC PASS. Dropbox original upload BLOCKED, no dual-provider claim.

## Scientific result

Positive reflected angular cell table, massless collisionless diagonal Bianchi I, Lambda0, u=t/Tstar, exact binary input. Fixed table mu[0,.5,1], phi[0,.25,.75,1], energies[[.1,.25,.05],[.2,.15,.15]], shear(.2,-.13,-.07), end=.08, 4 RK4 panels, refinement16 1536 rays. MPFR192 directed continuum-vs-recorded binary RK4 knot h error upper 3.7019164499698285e-6 < 1e-5, including CE1-F source 2.8664006500876736e-6, CE1-C whole-panel time + exact Hermite knot jumps 8.35515799694146e-7 and initial rounding. Other refinements1/2/4/8 FAIL fixed target. Independent GL40/DOP853 gap 6.543159869476511e-8 is not certificate.

## Verification

GitHub CI run https://github.com/cosmosapjw-quantum/bass/actions/runs/40790375589, 72 tests PASS and installed-wheel smoke PASS. New code Git blob 8daa44d413aca912edb0918d31caad6182ad2bd3, new tests blob b5eacd9ca23e0050a49a8774d39c0f2561f25d5e. Fresh clean parent source ZIP + CE1G_PATCH.diff apply, 72 tests PASS. Wolfram and SymPy 4th derivative identities zero. Distinct-author R6/C9 NOT_RUN; formally verified MPFR software, native Rust, full repository tests, production/physical input acquisition NOT_RUN.

## Resume instructions

1. Re-probe runtime; read current PR240 HEAD and sibling PR238/239, no automatic merges. Verify source ZIP SHA and manifest CRC/member SHA.
2. Read research/ce1g_20261029/{THEORY_KO.md,REPORT_KO.md,OPERATOR_CONTRACT.json,DAG_UPDATED.json,STAGE_LEDGER.json,SOURCE_MAP.json,HANDOFF_KO.md} and FINAL_DELIVERY_ACK_20261029.json.
3. Do distinct-author independent R6/C9 proof/code audit, specifically source pressure enclosure, Emax, generic positive-ray fourth derivative majorant, exact binary Hermite jumps, whole-path positivity/box and MPFR binding.
4. Do not replay full science unless necessary; reproduce scoped tests and saved evidence first. Do not use numerical DOP853 gap as a certificate.
5. Only after review choose CE1-H implementation-level MPFR assurance or separately source-locked collisional/polarized extension. Preserve 15 top-level nodes/21 edges and 9/15; CE-1 remains PARTIAL. No production/native promotion or main merge without independent gates.
