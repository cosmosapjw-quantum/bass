# FA03-C6: independent angular-source and grey-transport validation

2026-10-15 KST. Selected coding stage C6, with stage-local constructive theory: complex-azimuth regularity and conditional Fourier aliasing. Original R5–R10 theoretical dossier and C5 numeric records remain immutable. Active rei_bianchi is read-only.

New execution: 70-digit mpmath independent source coefficient at x=0.7. GL3x12 versus GL6x24 entry error 5.2616388014e-26; source spatially non-constant. 65-digit independent full grey S0 RK4 at 64 steps GL3x12 versus GL4x16 entry error 2.0433033364e-26; 50-digit and 32 steps gives 2.0433033199e-26. Both are empirical, not rigorous continuum integral bounds. C5 double precision cross-grid differences around 6e-16 reflect the floating-point floor, not exact angular independence.

New theorem input: fixed observer chi=1/125, psi=1/100, cap delta=1/50, real time x in [1/2,1]; strict elementary rational guards prove the angular source/operator and ODE solution holomorphic on complex |Im(phi)|<=4. Periodic N-point alias bound has a conditional factor 2/(exp(4N)-1). For N=12 this equals 2.85032816548e-21 multiplied by still-unknown M4. Actual M4 and radial GL3 interval bounds are NULL. cos(12phi) is a manufactured smooth alias counterexample: N12 gives 1 although true angular mean is zero.

C6 code includes high-precision source, high-precision grey ODE, rational analytic-strip guard, and an actual read-only REI checkpoint/owner liveness analyzer. C6 18/18 targeted tests pass following saved RED evidence and two targeted fixes; prior C5 15/15 tests remain unchanged. No native subagents were exposed or dispatched. No new REI solver was started, owner files were not modified.

Read REPORT_KO.md then HIGHPREC_FULL_GREY_S0_64.json, analytic_strip.py, REI_LIVE_READONLY.json, CODEX_HANDOFF_KO.md and NEXT_C7.json. Existing finite 36-ray R8 trace-norm certificate <4.75e-7 is unchanged; no continuity or physical atomic accuracy claim is promoted.