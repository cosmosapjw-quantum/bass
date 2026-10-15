# FA03 C8 next conversation integration handoff

Selected coding stage C8 is complete in its scoped numerical and reproducibility work. Do not ask local Codex to implement it: source and runs are in GitHub BASS research/fa03-c8-error-budget-20261015 built on C7 commit 049f615f29175e2fddd3860374dd23e2296a394b. All frozen FA02/FA03 hashes preserved.

Critical correction: early prospective bound discarded because frozen FA03 spectral k=L*x^(-2/3)*v includes observer L. Verified exact-rational replacement upper for complex energy disk is M=41931/20000, Re alpha >=411/625 and normalized GLn trace error <=(41931/9600)*25^(-2n). Never cite the invalid PRECORRECTION as an admitted result. GL4 bound2.8624896e-11, GL5 4.57998336e-14; these refer to exact ODE energy integration for real rays and normalized positive detector.

Local benchmark fixed exact original source, three epsilon cases, 128 time steps, GL4: 36ray4.47x,144ray7.43x,480ray10.85x versus original Jones GL8. Physically matched output <=2e-15 in measured settings, but full time/roundoff/continuous cap error not certified. 480ray tracemalloc peak GL4 2.170MB GL8 4.244MB; 2/4 threads slower; keep single worker. Source/weight/ODE float uncertainty remains unbounded. Exact-Fraction manufactured scalar-matrix RK4 Hermite residual trace bound demonstrated but DOES NOT prove real time-dependent FA03 RK4 global error.

C9 next: adversarial review of actual operator energy holomorphy, physical P3 trace assumptions, Jones contraction and proof versus code; inspect float-complex non-Hermitian continuation, original angular Jacobian and source L factor, actual measured CPU and memory. Do not waste next loop on redoing unchanged C5/6/7 tests except affected spots. C9 is NOT_EXECUTED here.

Parallel rei_bianchi is separate: AX07 scoped ZERO, AX08 signed incomplete, AX11/AX12 pending, admission NOT_ISSUED at latest verified snapshot; do not call a BASS toy spectral error certificate a cold H/He EoR whole-solver guarantee. Methodology from bass_cr curvature-directed Verner, rec_bianchi phase-volume, BASS_HE warm intervals, WU088_HH screen source cannot be transplanted without source-identity and physically matched input.
