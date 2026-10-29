# BASS CE1-M -> next conversation handoff

$physmath-research-loop $scispace $exa $wolfram

PROJECT=BASS
REPO=cosmosapjw-quantum/bass
NODE=CE1-M
PARENT_PR=251
PARENT_HEAD=cd7e7efdb384580ae44c0cdca873eba018a404e2
DONOR_PR=249
DONOR_HEAD=0370f99aea7cc457b32a3ebc259a343a82ac5a9f
BRANCH=research/bass-ce1m-source-local-physical-lock-20261029-r1
NEW_PR=READ_CURRENT_GITHUB_LINK_AND_FINAL_HEAD
UPPER_DAG=9/15
UPPER_CE1=PARTIAL
R_C_SCOPED=18/20
R6_C9_DISTINCT_AUTHOR=NOT_RUN
PRODUCTION_READY=false
MERGE_READY=false
AUTO_NEXT=false

## Original locked physics
Metric (-,+,+,+), Lambda=0, positive reflection-even massless collisionless diagonal Bianchi I, u=t/Tstar, ell_i=ln a_i, h_i=Tstar H_i. Exact original stored binary64: mu=[0,.5,1], phi_fraction=[0,.25,.75,1], E=[[.1,.25,.05],[.2,.15,.15]], shear=(.2,-.13,-.07). RK4 four panels, horizon .08, target max|delta h|<1e-5. No collision/tilt/polarization/general Bianchi/observed sky.

## Derived math
P_i(ell+s1)=exp(-4s)P_i(ell), same for positive continuum M and stored Q, hence D_i=P_i^M-P_i^Q obeys same common-scale law. For rigorously certified exact+Hermite lower logscale m_j and unchanged global upper B, eta_j=min(eta_global,exp(-4m_j)*E_Q(B-m_j1)); reject any B_i<m_j. Inherited CE1-I L_j=4Pmax(0)exp(-4m_j); positive 2x2 panel comparison with original initial/time/jumps and Emax unchanged.

## Actual current execution
Exact PR251 Git source blobs:
- bianchi/nonperturbative/einstein_tabulated_source.py: fdeb83a65cd424786ba6bb8ddadbcb2b2e2d45bf
- bianchi/nonperturbative/einstein_interval.py: abbab0990fdefaf535ccbf5191ae3e060cb19214
- bianchi/nonperturbative/einstein_tabulated_sharp.py: 61560ed52a78c01fe6f21923a7480af732d9ec4f
- PR249 source-local module blob: 1c905278f7a109e15f5e20d3ac7f931bdcf99433

Local RED: 4 FAIL,1 PASS before imported source domain repairs. After exact Git-blobs: 107/107 tests PASS, exit0 (12 focused modules). Wolfram independent algebra returned {1,0} for common pressure scaling/Jacobian row sum. Native subagent NOT_EXPOSED.

New fresh ref8 384 rays all source+time: source_h=8.595820125315265e-6, time+jump_h=8.157313590378725e-7, total_h=9.411551484445186e-6, MET. Same original target.

New ref16 1536 rays fresh four-panel MPFR192 SOURCE bound plus exact SHA match to PR246/PR251 stored ray mass and RK4/Hermite path; inherited SHA-verified initial/time/jump budget (not newly rerun full time residual): source_h=2.1459172502504843e-6, initial_h=1.865856997285437e-16, time+jump_h=8.158297286595899e-7, total_h=2.9617469790966602e-6, MET. No formal Python/MPFR program-level proof.

Inherited original upper DAG 9/15 (15 nodes,21 edges), CE1 PARTIAL; no top-level node promotion. RF00, RF-BENCH, CE1-L etc all succeeded on PR251 final HEAD in previous check, but new CE1-M final HEAD CI MUST be independently read. Distinct author R6/C9 still NOT_RUN; no verified production wheel, measured sky or native transport. No parent/main merge.

## Restore/run
1. Fetch live PR HEAD/branch of new Draft. Compare source/test Git blobs, parent SHA and raw ZIP manifest.
2. Validate original physical-source lock, positive current masses and shape/cardinality on actual final head.
3. Run `research/ce1m_20261029/REPRODUCE.sh` under pinned Python deps. Verify ref8/fresh source/full time; for ref16 reuse only with exact source/path identity or rerun in four isolated MPFR processes.
4. Read `THEORY_KO.md`, `REPORT_KO.md`, `SOURCE_IDENTITY.json`, `RESULTS.json`, `DAG_DELTA.json`, `STAGE_LEDGER.json`. Archive CRC/payload hashes and remote ACKs.
5. Next bounded unit: genuine independent distinct-author proof/code review (R6/C9), or formal implementation-level MPFR ctypes interval assurance. Do not repeat the same internal review recursively. Stop after one bounded unit.
