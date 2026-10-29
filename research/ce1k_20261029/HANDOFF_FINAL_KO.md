# BASS CE1-K → NEXT THREAD HANDOFF (2026-10-29)

$physmath-research-loop $scispace $exa $wolfram

PROJECT=BASS
REPO=cosmosapjw-quantum/bass
UNIT=CE1K_CANONICAL_TIME_LOCAL_SOURCE
BASE_PR=246
BASE_SHA=4474f8acb13614ffda7a30524a815976e306efc9
DONOR_PR=247
DONOR_SHA=bd94bf270dcbf3bf140ac6cf7a7caf7e72532ac0
EXPECTED_BRANCH=research/bass-ce1k-canonical-local-source-20261029-r1
UPPER_DAG=9/15
UPPER_EDGES=21
UPPER_CE1=PARTIAL
R_C_STAGE_OUTPUTS=18/20 scoped; R6/C9 distinct-author NOT_RUN
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false
NATIVE_SUBAGENTS=NOT_EXPOSED

## Immutable physics
Metric (-,+,+,+), Lambda=0, massless collisionless reflection-even diagonal Bianchi I, positive exact-binary64 original six angular cells. Normal proper u=t/Tstar, ell=ln a, h=Tstar H. mu=[0,.5,1], phi fractions=[0,.25,.75,1], energies=[[.1,.25,.05],[.2,.15,.15]], shear=(.2,-.13,-.07), horizon=.08, RK4 panels=4, target max|Delta h|<1e-5. Keep Emax in source/geometry; preserve all exact-binary Hermite knot jumps, original source/path.

## Mathematical result
Original positive continuous/angular-cell M and stored exact-real binary ray/mass Q pressure have common homogeneity P(ell+s1)=exp(-4s)P(ell). Hence D=P_M-P_Q has the same transformation. Canonical PR246 proves shared exact and cubic path panel lower m_j. With original geometry B, eta_j=min(eta_global,exp(-4m_j)*E_Q(B-m_j 1)), outward MPFR192, require B_i>=m_j or reject. Reuse canonical PR246 L_j pressure Lipschitz cap and 2x2 positive Dini propagator. Physical RHS not changed.

## Actual science (CURRENT RUN)
Full fresh source+time local computations ref1,2,4,8: CE1-K h-upper [5.256210833627636e-4,1.3745837526157558e-4,3.522096821063855e-5,9.411551484445186e-6], target only ref8 MET, ray counts [6,24,96,384]. Ref16: source+path SHA matched canonical PR246 4-worker OS MPFR192 evidence; *fresh* source MPFR192 caps 3.569278983301304e-05, 2.9241709495299544e-05, 2.358366230872103e-05, 1.861256875971887e-05. Source h=2.1459172502504843e-06; SHA-verified inherited parent time+jump h=8.158297286595899e-07; total outward upper 2.9617469790966602e-06, MET. **Not fresh whole-panel time residual**, not formal Python/MPFR program verification. Prior source script final JSON writer error (shadowed time) fixed but rerun not performed; fresh MPFR source captured to log and interval-reassembled, proof record REF16_SOURCE_ONLY.json.

## Executed code and tests
New opt-in `bianchi/nonperturbative/einstein_tabulated_source_canonical.py` imports PR246 authoritative unchanged source, interval and local code. Tests `tests/nonperturbative/test_ce1k_canonical_source_local.py`; all 102 targeted tests PASS, test log `research/ce1k_20261029/FULL_SCOPED_TESTS.log`; frozen canonical blobs exact. Wolfram pressure ratio/derivative (1, 0). Native Rust/full repository/RF-00 and RF-BENCH-00 policy gate not admitted. PR246 and PR247 source themselves are not auto merged.

## Resume executable actions
1. Re-read live branch/PR head and GitHub CI; treat source records as snapshots until fresh read.
2. Read THEORY_KO.md, REPORT_KO.md, DAG_DELTA.json, R0_SOURCE_LOCK.json, REF16_SOURCE_ONLY.json, SWEEP_IN_PROGRESS.json, 20 stage records/backups and MANIFEST.
3. Run `PYTHONPATH=. bash research/ce1k_20261029/REPRODUCE.sh` in the isolated branch with scipy1.17.0 numpy2.3.5 pytest9.0.2, MPFR192 lib. Ref16 source-only recovery script requires the pinned PR246 S2 ZIP via its path, and no new full-time proof is claimed.
4. Independent distinct-author physics R6 and code C9, RF-00/RF-BENCH-00 root failure diagnosis; do not grant reviewer independence from same-model repeat or 4 OS workers. No merge unless all actual claim gates are met.
5. Upper DAG 9/15 unchanged until CE-1 top-level physical+implementation acceptance. If a new scientific node is requested, pick one bounded dependency-admissible next node after this review and full provenance check. Handoff after that node.

## Backup/publishing
Per-stage Git/Drive/Dropbox RECEIPTS must be verified in the new thread. This handoff is generated before remote publication, so publication fields are NOT YET VERIFIED; use final publishing receipt in the package. Never infer dual provider from local ZIP.