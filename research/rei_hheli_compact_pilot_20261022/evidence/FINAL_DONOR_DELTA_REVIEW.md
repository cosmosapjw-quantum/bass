# Final donor delta review

Checked 2026-10-21 16:05:51 UTC. Read-only GitHub fetches succeeded for both pinned old→new comparisons and all four complete recursive trees; no tree truncation. REC compare returned only300 files, so full blob-tree comparison was used (628 changed files). HE has81 changed files.

## REC

`a949529872eb5ba0e20c7e206fe893e5d544e48c` → `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7` (2 commits). Latest `research/rec_rei_hheli_sandbox_20261021/REPORT_KO.md` and `evidence/INDEPENDENT_FINAL_REVIEW.json` establish125 main+1 opacity-off unique IVPs, z20→2,193 saved nodes. The main grid is5×5×5 in Sigma0/Pm0/Pr0. First main trajectory was recovered without rerun. There are127 added trajectory paths because historical failed/recovered copies remain; this is126 unique IVPs.

Only existing scientific-directory change is `code/coupled.py`: JSON serializer now converts NumPy scalar via `.item()`. Blob `7d1a346081528f7f9449fdcb1032cf84a9aabb44`→`e95860973a4e0cd9e03b8b09e134ab668eba58b1`. Exact old/new contents were fetched. No RHS/Jacobian/geometry/atomic-rate/vendor/model changes in complete tree delta. New CONTROL_CAMPAIGN.json is run configuration. Physical HOLD,global convergence NOT_RUN,production NOT_APPROVED and historical REC HOLD remain.

## HE

`e8bb035d31f59e34734947b9082bdbd60128b799`→`0c016a11966547d81dbc61117ab45e8f0ab81790` (1 commit). Adds new52-state primordial/atomic/coupled implementation and rate/scenario tables. Existing compact_transport and scientific/vendor blobs are unchanged. No new science trajectory or results tree exists at this pinned head. `evidence/execution/PREFLIGHT_CONTRACT.json` is preflight only (3 nominal+2 L24 guards); DAG F.C7–F.C10 pending. Independent coupled review/repair explicitly report science_ivp_runs=0. Repair passes three saved derivative points with unchanged RHS,maximum scaled discrepancy2.9392582460860647e-8; this is not an IVP run.

## Effect on this pilot

Retain immutable REC a949 full62 kernel pin and HE mathematical-idea-only attribution. Latest REC is now executed,so earlier unexecuted wording applies only to our historical intake pin. Its126 trajectories are separate from our127 local IVPs. HE additions are not imported. No adoption or HOLD reset is justified by this intake. No ODE or benchmark was run. Detailed exact paths,blob identities and successful fetched review content are in FINAL_DONOR_DELTA_REVIEW.json.

