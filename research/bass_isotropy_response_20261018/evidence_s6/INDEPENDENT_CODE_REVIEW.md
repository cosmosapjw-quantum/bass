# Independent S6 code review (read-and-run only)

Reviewer: separate subagent (physmath scientific-diff-reviewer), 2026-10-19, on untracked S6 files before commit 18a4f96.
Scratch re-runs: holdout rows byte-identical; finite_d tables/certificates byte-identical to r2 (still FAIL on G5);
spectral native_output_sha256 identical; prereg predictions equal spectral_residual.predicted(); 18 tests OK.
No swallowed errors; no tolerance widening (moment gate 3e-15, positive weights). Existing verified files unchanged.

Findings (most severe first) and disposition:

1. MAJOR run_s6_finite_d.py G3 tautological (bound uses rule's own series; 1e-12 relative slack ~1e10x ARITH_FLOOR).
   -> FIXED in r3: G3a sign-free bound sum|k_l M_l|/F + tail + floor and G3b theorem (S6.4) with only constrained
   low moments; mp comparison, no relative slack. 910 S6.4 points, min bound/actual 3.47.
2. MAJOR run_spectral_refinement.py prereg partly enforced (prereg not pinned/committed; probe/runner edited after prereg;
   26 rows hard-coded; MAPPING gate not in prereg). -> FIXED: PREREGISTRATION_R2.json pins 9 file SHA256, row grid,
   all gates; runner requires it committed clean in git; run02 after commit 18a4f96; identical native output.
3. MAJOR streamed json.dump can leave partial receipt; attempt0 receipt truncated yet contains "PASS_SCOPED".
   -> FIXED: s6_io.write_json_once; attempt0 file renamed *.TRUNCATED_PARTIAL.json with NOTE.json.
4. MINOR holdout receipt source sha was pre-ARITH_FLOOR. -> FIXED: refinement_holdout_r2 (rows byte-identical).
5. MINOR rank1 path accepted non-UNRESOLVED float statuses; 2^-48 width undisclosed. -> FIXED: only
   FEASIBILITY_UNRESOLVED_RANK1 routed; width documented in code and S6 docs. Exact part judged sound.
6. MINOR _int accepted ' 3 ' and '-3_0'. -> FIXED: regex -?[0-9]+ only.
7. MINOR RAM/disk/wall limits recorded not enforced. -> FIXED: s6_io.apply_limits + disk check.
8. MINOR artifact sha build-path dependent. -> receipt note added; reproducibility key is native output SHA256.
9. MINOR test gaps. -> added vertex AMBIGUOUS, decided-status rejection, validator grid/tamper, partial-receipt tests (22 total).
   Rank-one path has no real-campaign use (0 UNRESOLVED_RANK1 rows) — stated in results.

Reviewer verdict at review time: numerics correct and reproducible; not ready to promote until 1–3 fixed. All fixed above.
