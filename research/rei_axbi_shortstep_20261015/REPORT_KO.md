# REI AX03 C8: 짧은 고유시간 구간의 안정적 적분과 정확도·성능

2026-10-15 KST. 기존 BASS PR #156, REI PR #121의 AX03 배경 공급을 이어서 코딩 연구 C8 수치·재현성 단계 실행. 원래 rei_bianchi 생산용 Rust background/driver는 미변경. 별도 local Codex를 호출하지 않고 이 대화에서 사용자 Ubuntu 상의 Python/Rust를 실행. Native subagent=NOT_RUN_TOOL_UNEXPOSED.

## 물리적 source lock

동일한 REI BACKGROUND_FAMILY_LOCK SHA256 46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0. 비틸트 축대칭 Bianchi I, (-,+,+,+), zbar20 -> zbar4, 경과 SI 고유시간, q_ref=0,+/-0.005,+/-0.01 PhysicalDensityFixed 및 별도 SAME_H(.01) counterfactual.

H_F(a)=H0 sqrt(Omega_m/a^3+Omega_r/a^4+OmegaLambda), s(a)=q_ref H_F(a_ref)(a_ref/a)^3, H=sqrt(H_F^2+s^2); dt/dln(a)=1/H, db/dln(a)=s/H.

Numerically stable proper-time and shear intervals are evaluated as PHYSICAL LOCAL INTEGRALS
Delta t=Integral_{ln(a0)}^{ln(a1)} dx/H(x), Delta b=Integral dx s/H,
where delta x=log1p((a1-a0)/a0). In each Gauss panel a=a0 exp(theta*delta x), avoiding subtraction of large accumulated 1e16 second clocks. Gauss4 and Gauss8 are distinct numerical integrators, NOT rigorous whole-domain interval-error enclosures.

Hermite clock uses source table 501 nodes with *physical endpoint derivatives* in x. Its cubic power coefficients c0=y0,c1=h d0,c2=3(y1-y0)-h(2d0+d1),c3=-2(y1-y0)+h(d0+d1). The difference is evaluated in factored form:
p(u+delta)-p(u)=delta*[c1+(2u+delta)c2+(3u²+3u delta+delta²)c3].
Wolfram 15.0.1 independently reduced this polynomial identity to exact zero. Every t cell's derivative quadratic has its mathematical minimum checked strictly positive. q=0 has identically zero b; nonzero q checks b' preserves physical sign. The table is not silently clipped or extrapolated.

## First scientific counterexample and 90 high-precision checks

Physical q=+.01 at a0=.1 and next representable binary64 a1=.10000000000000002:
- GL4 delta t=3.5706700623663608 seconds.
- Independent GL8 same displayed value.
- Hermite factored delta t=3.5706700623580856 seconds.
- accumulated t(a1)-t(a0) computed in double precision=4.0 seconds, around 12% error.

Independent mpmath 80-digit exact dyadic binary64 input endpoints sampled 6 models x 3 reference scales (.05,.1,.18) x 5 interval widths (1e-4,1e-8,1e-10,1e-12,nextfloat), 90 intervals:
- Max proper Delta-t relative error local scalar Gauss4: 2.2903079824291173e-16.
- Max Delta-b relative error local scalar Gauss4: 2.5734772941032376e-16.
- Max proper Delta-t relative error Hermite501: 5.794301303454278e-10.
- Max Delta-b relative error Hermite501: 5.774119270322933e-10.
- Max accumulated timestamp subtraction relative error: 1.2404637264237184 (124%).
- 57/90 naive subtraction intervals failed relative 1e-8 although local physical GL4 remained <1e-10.
These are source-scoped sample observables, not a mathematical uniform error certificate.

Separately compiled stdlib-only independent Rust GL4, same frozen physical family and 90 input endpoints: max dt relative error vs mpmath80 2.2903079824291173e-16, db 5.101904131078777e-16. Illegal q_ref input rejected exit3 with Q_NOT_FROZEN. No original Rust owner source was copied into a new fake production acceptance.

## Historical REI HOLD remains a live integration obligation

Original rei_bianchi performance/background_table_001 BENCHMARK_RECEIPT frozen source snapshot recorded status COMPONENT_GATES_PASS_SHORT_STEP_SUBTRACTION_HOLD. Its prior sampled stable Rust table interval increments have max relative discrepancy 2.3826052242270634e-11, while its actual cumulative timestamp subtraction had max relative discrepancy 2.245989675930815e-5, and 356 explicit short-step holds. The prior Rust table's sampled stable increment is MORE accurate than this new 501-node Hermite; do not claim the latter is the best incumbent algorithm.

This C8 offers another independent direct quadrature and interval-scoped API, but does not fix production simply by existing: actual driver must stop subtracting cumulative timestamps and be separately native-tested after explicitly authorized integration. The former production gate remains HOLD until actual driver callsite/source is changed and tested.

## Matching-accuracy CPU/memory/parallelism

Actual Ubuntu matched source, 90 physical intervals, cached/background constructors excluded from 5 warmed medians:
- Historical unsafe naive cumulative subtraction ~0.02911 s.
- Hermite stable incremental ~0.0004661 s.
- Cached scalar physical GL4 ~0.005441 s.
- Grouped NumPy vectorized physical GL4 workers1 ~0.0006356 s.
- Grouped vector GL4 worker2 ~0.0013199 s.
- Grouped vector GL4 worker4 ~0.0012837 s.

An earlier distinct within-host source benchmark before GL node caching had scalar physical GL4 0.013793 s and after a later run 0.003814 s, meaning node cache is a productive overhead reduction but ratio across different timing rounds is not a guaranteed fixed speedup. Vectorized GL4 agrees to source scalar and mp80 within 3e-13 on the tested real endpoints. Actual parallel 2/4 worker threads did not accelerate this small workload: stay workers1.

No native EoR chemistry speedup is asserted. Hermite requires one-time 6-case DOP853 and table construction; those setup costs and process RSS are not hidden inside one per-query benchmark.

## Photon exact Killing map and clock physics

For Delta b=b_late-b_early computed directly from local source s/H, Delta x=ln(a_late/a_early) from log1p, the earlier/late photon energy log ratio is

log(E_early/E_late)=Delta x + 1/2 log1p[(1-mu_late²)expm1(-2 Delta b)+mu_late² expm1(4 Delta b)].

The reverse ray cosine is mu_early=mu_late exp(2 Delta b- (log E ratio-Delta x)). Its angular Jacobian log is -3(log E ratio-Delta x), and therefore the phase-volume identity 3 log(E_early/E_late)+log J-3 Delta x=0. Wolfram exact symbolic residual zero and original BASS AX03 frozen photon_pullback comparison PASS. This is collisionless directional photon propagation only; no physical ionizing source/collisions imported.

New source-locked background clock fixed-a vs fixed-proper-time diagnostics: q=+.01 has end Delta t(q)-Delta t(0)=-249032577712 seconds at same mean scale a=.2, and max absolute Delta ln(a) at overlapping same proper time 8.33718636e-6; q=+.005 has end difference -62259467800 seconds and max Delta ln(a) 2.08435522e-6. Both even under q->-q. REI PR #119 and PR #122 have independently found actual HII abundance response much greater at fixed proper time than at matched mean scale a; our geometry-only results give physical context, but no HII or Tgas was recalculated here and no AX11 error certificate was produced.

## Execution record and positive closure

New local stage C8 29/29 tests PASS including source SHA, 90-source high precision, independent Rust physical parity and illegal-input exit3, signed parity, Hermite derivative/monotonicity, cancellation example, vector/2-4-thread matched outputs and clock/optical invariant. Previous supplier stage C5-C7 targeted 33 tests retained and remain separate. Wolfram exact Hermite/phase-volume/positive GL4 identity checked via tool. Native subagent unavailable; no fabricated parallel reviewer. Actual user Ubuntu source/data/plots preserved.

C8 numerical/reproducibility scope COMPLETE. Still NOT verified: rigorous global enclosure of all possible short intervals, complete floating input/interpolation kernel roundoff, replacement of live Rust AX03 driver call sites, full ionizing radiation feedback, native H/He abundance scientific admission. Next legitimate stage C9 evaluates the actual boundary of production integration and true short-increment ABI; not auto-executed. Existing original AX03 constraints and source clock must remain authoritative.
