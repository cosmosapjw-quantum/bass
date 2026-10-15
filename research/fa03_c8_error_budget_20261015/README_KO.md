# FA03 C8: rigorous energy GL error + measured numerical/resource survey

Selected coding stage C8 from parent C7 commit 049f615f29175e2fddd3860374dd23e2296a394b. New theory, actual local Ubuntu scientific code execution, memory optimization, vectorized energy orders and real measured 1/2/4-thread ray partitions. Separate local Codex NOT_USED; native subagent dispatch unavailable (NOT_RUN). Frozen original R7 FA02/FA03 source and R8 fixed36 ray trace-norm <4.75e-7 untouched.

New theorem with the important real observer factor k=L*x^(-2/3)*v: for normalized Gauss–Legendre n-point energy integration of the **exact frozen FA03 continuous-time ODE** on real-angle rays,
    trace_norm_error <= (41931/9600)*25**(-2*n).
Thus GL4 <=2.8624896e-11, GL5 <=4.57998336e-14, GL6 <=7.327973376e-17. This does not certify floating weights, RK4, continuum angular cap or empirical opacity. The original derivation that accidentally dropped L has an actual observed RED source-violation test and both original PRECORRECTION evidence JSONs are preserved. The corrected physical rule is exact-rational and Wolfram15.0.1 checked.

Additional exact Fraction manufactured matrix RK4 Hermite-Bernstein L1 defect bound tests contractive propagation under constant passive source; 64step bound7.39049e-10 contains its actual independent high-precision error ~1.51e-12. This **is not** a bound for the time-varying real FA03 ODE.

Real FA03 execution: at 36/144/480 rays, energy GL2/3/4/5/6/8 vs GL24 and RK4 16/32/64/128/256/512 vs1024; reports source-matched actual deviations without numerical certification of full ODE or angle continuum. 128 RK4: GL4 real Stokes vs original separate Jones GL8 actually accelerates 4.47x/7.43x/10.85x respectively; within real Stokes at480, GL4 0.139s vs GL8 0.187s (same host measured); tracemalloc peak2.17 vs4.24MB. 2/4threads were executed and slower. C7 selected original same-source code remains unchanged.

Run:
    python3 research/fa03_c8_error_budget_20261015/spectral_cert.py --target 1e-10
    python3 research/fa03_c8_error_budget_20261015/manufactured_defect.py
    python3 -m unittest discover -s research/fa03_c8_error_budget_20261015 -p test_c8.py -v
    python3 research/fa03_c8_error_budget_20261015/convergence_c8.py --out /tmp/C8_repeat_full.json
    python3 research/fa03_c8_error_budget_20261015/resource_probe.py --out /tmp/C8_repeat_resources.json

Read REPORT_KO.md for theorem/proof/limitations and evidence/ for true host measurements. Original C7 34, C6 18 and C5 15 tests are inherited and must remain green. Wolfram native xAct 1.3.0 7 scoped zero identities. C9 remains next INCOMPLETE stage; no automatic next loop, active rei_bianchi and native solver not modified.
