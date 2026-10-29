# CE1-J S2: three-way source/time reconciliation, physical replay and stop

**2026-10-29 | Draft PR246 | Parent PR245 HEAD** `9cd3063b0c411a0289f6975659906fd1f64b2817`.

## Actual repaired code and scope
The CE1-G interval module is the exact PR244 safe-current-source blob `3a3f384e793a59f0779cb09a21dd74c1ae7d0c3a`; the CE1-G time module is the exact PR244 left-knot-check blob `b2047a7a7fd64e8a1148d242ee32840f648184b5`. PR243's independently established mutable-mass/ray issue is covered without merging its separate branch. The CE1-I local wrapper `einstein_tabulated_local.py` now has no redundant stale cache rejection or duplicate Hermite origin assertion. The old mutation test was made to prove current-source recertification. Same physical RHS, exact-binary inputs, MPFR192, RK4 coefficients, positivity box, Hamiltonian initial root, fixed target `max_i|Delta h_i|<1e-5` and six-cell original table.

## RED/GREEN and CI
Baseline after importing PR244 but before updating CE1-I: **91 PASS, 1 FAIL** from legacy cache-rejection expectation. After minimal reconciliation: **95 focused PASS**, Python 3.13.5. GitHub Actions [run 40827179395](https://github.com/cosmosapjw-quantum/bass/actions/runs/40827179395) SUCCESS, **95 passed in 16.81s**; installed wheel printed `CE1J_WHEEL_SAME_PHYSICS_AND_FRESH_SOURCE_PASS`. CE1C separate workflow succeeded. RF-00 and RF-BENCH-00 failed on this scoped head; no root merge admission.

## Actual scientific evidence
Positive collisionless diagonal expanding Bianchi I (signature `(-,+,+,+)`, `u=t/Tstar`, `h_i=Tstar H_i`), Lambda0, eight-reflected first-octant positive piecewise-constant angular energy. Four RK4 panels, frozen `mu=[0,.5,1]`, `phi_fraction=[0,.25,.75,1]`, energies `[[.1,.25,.05],[.2,.15,.15]]`, shear `(.2,-.13,-.07)`, `u<=.08`.

Refinement8, 384 grouped rays: CE1-G `1.2322918653868093e-5`, CE1-H `1.227583245284329e-5`, CE1-I `1.2273903547843227e-5`: **target NOT_MET**.

Refinement16, 1536 grouped rays: from four separate OS MPFR192 panel workers with **source rays+mass+recorded RK4 state+Hermite coefficient exact SHA identity**, reassembled through the same positive 2x2 nonlinear Dini comparison and binary Hermite knot jumps:
- CE1-G `3.7019164499698285e-6`
- CE1-H `3.675931156248731e-6`
- CE1-I `3.6749116877624083e-6`

All three differ from the pinned historical original by **exactly zero** in the recorded float outputs; target MET. Panel-local Lipschitz coefficients `[1.3000000000000003,1.257046869944473,1.2168561190192664,1.1792092149491518]`. Current full PR244-exact-source four-worker wall time ~23.48s (not a generalized speedup). A monolithic ref16 Python attempt failed the current execution's 120s timeout, separately preserved as `EXECUTION_FAILED`, not numerical or mathematical refutation. An experimental full-byte-keyed cache did **not** reliably remove this runtime stall, so was **NOT adopted**; authoritative PR244 source bytes remain untouched.

## Adversarial plot reading
One plot shows descending panel Lipschitz coefficients; another shows refinement8 fail vs refinement16 success at the **same 1e-5 target**. G/H/I lines overlap visually because their differences are subpercent, not because the bounds are identical.

## Verdict and exact next condition
`COMPLETE_SCOPED_CANONICAL_CANDIDATE_RECONCILIATION`, **upper DAG 9/15**, CE-1 PARTIAL. Python/MPFR program formal proof, independent distinct-author R6/C9, native Rust, full RF-00/RF-BENCH-00 policy CI, production/merge readiness all NOT_ADMITTED. No other PR or main modified. Do **not** auto-merge variants; next genuinely useful bounded unit is independent-source scientific/code review plus root-policy failure diagnosis before any merge gate. Per-stage artifact ZIPs are immutable and delivered with separate Git/Drive/Dropbox receipts. S2 research ZIP `BASS_CE1J_S2_FINAL_20261029.zip`, **225,206 bytes, 30 members, SHA256 `c25092d1316763b16cec8971ae9e44b47ba2fefe0efdedcf0d0fac5a345c8b82`**, CRC+member SHA manifest checked.
