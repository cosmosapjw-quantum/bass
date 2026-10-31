# CE1AJ research handoff, scoped and reproducible

PROJECT=cosmosapjw-quantum/bass
UNIT=CE1AJ_CONTINUUM_FINITE_U_DARK_SOURCE_L4
CURRENT_PR=290
PARENT_PR=288
IMMUTABLE_PARENT_HEAD=06a89b70200c09e44711235ef6d01a0b797b2a03
ORIGINAL_SOURCE_SHA256=022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035
MODEL=diagonal Bianchi I massless collisionless Einstein-Vlasov, Lambda 0, metric (-,+,+,+)
TIME=u=t/Tstar, original domain [0,2/25]
DARK_INTEGER=[[53,-106,53],[-203,406,-203]]/406

SCOPED_ANALYTIC_CLAIM=d_epsilon alpha42(u)|epsilon0 < -u/2 for 0<u<=1e-6
CONSTRUCTIVE_COMPARISON=-3u/4+232225u^2
CONTINUUM_5x5_FINITE_TIME_RANK=NOT_CERTIFIED
FULL_HORIZON_U_0_TO_0p08_SIGN=NUMERIC_ONLY

NEW_BASELINE_STATES=2406
NEW_DARK_TANGENT_RECORDS=2406
NEW_GENUINE_NONLINEAR_PLUS_MINUS_SOURCE_FAMILY_STATES=4812
NEW_PHYSICAL_RECORDS_TOTAL=9624
NEW_SCIENTIFIC_PLOTS=5
GL=6,8,16
TWO_WINDOWS=401 epochs [0,1e-6] and 401 epochs [0,0.08]
LOCAL_TESTS_ORIGINAL_SOURCE_INCLUSIVE=95/95_PASS
GITHUB_CI=READ_ACTUAL_FINAL_HEAD_RUN_BEFORE_ASSERTING_SUCCESS
NATIVE_SUBAGENT=NOT_RUN
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
UPPER_DAG=9/15
UPPER_EDGES=21
CE1=PARTIAL
SCOPED_INHERITED_R_C=18/20
NEW_UPPER_NODES=0
PRODUCTION=HOLD
MERGE=HOLD
AUTO_NEXT=false
STOP_AFTER_ONE_BOUNDED_UNIT=true

The actual code, derivation and CI recipe are in research/ce1aj_20261031. The Git workflow recreates all physical CSV, figures, source-included archives, and 20 stage-specific ZIP checkpoints, then uploads one GitHub Actions artifact. Preserve the initial failed CI if any, use only actual provider acknowledgment and SHA readback to report double backup. The original CE1AI PR and other branches are not to be merged or updated by this successor.

**Next possible science (NOT auto-authorized):** materially widen the strict finite-u continuum interval using sharper source/Einstein bounds or interval ODE enclosure; or certify the full 5x5 source→l2/l4 finite-time determinant. Independent distinct-author mathematical and code review remains missing for upper acceptance. No additional user-provided literature is essential for the bounded CE1AJ result. Context papers: Rendall gr-qc/9505017; Heinzle & Uggla CQG (2006) DOI 10.1088/0264-9381/23/10/016; Lee, Nungesser & Tod GRG (2020) DOI 10.1007/s10714-020-02699-7; Barzegar, Fajman & Heißel PRD (2020) arXiv:1904.13290.
