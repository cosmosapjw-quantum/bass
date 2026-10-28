# BASS CE1-G 연구 보고서: positive angular table + MPFR whole-panel time certificate

**2026-10-29 | Parent:** `cosmosapjw-quantum/bass` PR239, HEAD `9de0f37955f259b5e9172ce406d1353bf7cc3695` | **New:** Draft PR240, isolated `research/bass-ce1g-tabulated-wholepath-20261029`.

## 결론과 범위

기존 CE1-F의 양의 piecewise-constant 각분포 표에 대해, **원래의 동일한 continuum angular function**을 유지하면서 각격자 세분화가 만든 exact-real stored-ray source error, 초기 Hamiltonian root의 binary rounding 차이, 저장된 RK4/Hermite 경로의 전구간 time defect 및 작은 Hermite knot jump를 MPFR192 외향구간으로 합성했다. 이는 선택한 massless collisionless diagonal Bianchi-I nonlinear Einstein–Vlasov 문제의 **기록된 수치 궤적**과 정확한 continuum ODE 해 사이의 조건부 수학적 오차 상계다.

Metric signature(-,+,+,+), u=t/Tstar, ell_i=ln a_i, h_i=Tstar H_i, E,P_i=(8piG Tstar²/c²) 곱하기 energy density/pressure. Lambda=0. Normal observer frame. No small-shear approximation, angular multipole closure, matter collisions, native solver migration, spatial EFE, projection or clipping.

**사전 고정 입력:** `mu=[0,.5,1]`, `phi_fraction=[0,.25,.75,1]`, `cell_energy=[[.1,.25,.05],[.2,.15,.15]]`, shear=(.2,-.13,-.07), u=0..0.08, 4 RK4 panels, 1 exact-rational subcell per panel. Refinement 1,2,4,8,16; target `max_i |Delta h_i|<1e-5`. Stored decimal-looking Python floats are treated as exact binary data; continuum reference is the corresponding exact-binary piecewise-constant cell table, not ideal decimal acquisition.

## 이론적 성과

`P_i(ell)=exp(-sum ell) integral [exp(-2ell_i)n_i²/sqrt(sum exp(-2ell_j)n_j²)]dmu`, `sum_i P_i=E`, `sum_j |partial P_i/partial ell_j|=4P_i<=4E0` in expanding sector. The Hamiltonian constraint obeys `C'=-2theta C`. For recorded Hermite `tilde z` define `r_ell=tilde ell'-tilde h`, `r_h=tilde h'+tilde theta tilde h-P_Q(tilde ell)`. The CE1-C Taylor3+analytic-fourth majorant applies to **any positive stored ray/mass measure** because it only uses the bound `sum w||ray||`, not a polynomial angular ansatz. SymPy and Wolfram verified both fourth-derivative coefficient identities (0 residual).

**수정한 엄밀성 경계:** binary64로 계산한 Hermite cubic coefficient는 exact-real 의미에서 다음 저장 knot를 정확히 보간하지 않을 수 있다. `j_i=sum_{k=0}^3 c_{ik}-y_{i+1}`를 MPFR 외향 계산하고 매 panel 끝의 상태 오차에 추가했다. 이를 생략한 전구간 잔차 전파는 수학적으로 충분하지 않다. 실제 jump는 이 fixture에서 ~1e-17 수준이지만 엄밀성은 크기와 무관하다.

비선형 Dini 비교계는 `D+e_ell<=e_h+rho_ell`, `D+e_h<=4Emax e_ell+eta_Q+rho_h`이고, initial/source/time+jumps 세 양의 기여를 분리해 hyperbolic 2×2 propagator로 전파한다. True continuum box는 `h_i<=h_i(0)+E0u`, `ell_i<=h_i(0)u+E0u²/2`; stored cubic path box는 외향 Bernstein hull. 두 영역의 합집합에서 source bound를 평가하므로 sampled endpoint의 positivity를 근거로 삼지 않는다.

## 실제 실행 결과

| refinement | rays | source h upper | time+jump h upper | combined h upper | target |
|---:|---:|---:|---:|---:|---|
| 1 | 6 | 7.06345786932125e-4 | 8.271557342055911e-7 | 7.071729426664234e-4 | FAIL |
| 2 | 24 | 1.8316580159770366e-4 | 8.334304028268818e-7 | 1.839992320006233e-4 | FAIL |
| 4 | 96 | 4.602588565464722e-5 | 8.350164971726358e-7 | 4.6860902151951716e-5 | FAIL |
| 8 | 384 | 1.1487502870674648e-5 | 8.354157831006931e-7 | 1.2322918653868093e-5 | FAIL |
| 16 | 1536 | 2.8664006500876736e-6 | 8.35515799694146e-7 | **3.7019164499698285e-6** | **PASS** |

위 값은 `max_i |Tstar Delta H_i|`의 외향 상계이며, 실측 두 수치해 차이가 아니다. Ref16 계산 wall time 약 53.46초, 모두 동일 4개 RK4 panel. 시간적분 기여는 세분화와 거의 무관하고 source 기여가 감소한다. Source-only CE1-F bound 2.8664e-6를 실제 computed path bound로 잘못 승격하지 않고 time/jumps를 추가했다.

**독립 알고리즘 falsification:** 원래 6개 physical cell에서 GL40×40 독립 각구적을 구축하고 DOP853 `rtol=2e-13,atol=2e-15`로 적분한 후, ref16 저장 RK4 endpoint와 비교한 `max_i|Delta h_i|=6.543159869476511e-8`는 계산 상계보다 작았다. 이는 검증용 수치 대조일 뿐 continuum reference 자체의 interval certificate가 아니다.

## 검증 및 실패 보존

- Python execution probe: PYTHON_PASS; libmpfr.so.6 present. Existing CE1-F archive 14,531,847 bytes/291 members SHA256 `3fffaab45822058088b1e87f2c6692e969d33f3c0ebc4b091be3987435c54f4d`, ZIP CRC PASS.
- Parent inherited tests: 52 PASS. New tests: 15 PASS. Additional inherited physical input tests included: total 72 PASS locally (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`). The first new test run had **14 PASS, 1 FAIL** because a test incorrectly demanded rejection of a modified stored mass; the correct mathematical contract admits arbitrary recorded approximants and must pay for their residual/source discrepancy. Repaired only the test to demand increased certified error; final 15 PASS, original failure retained.
- Initial probe lacked `PYTHONPATH=.` when run as a standalone script; `ModuleNotFoundError` is environment/test invocation, not physics failure. Repaired invocation; no source physics change.
- A resource-limited combined ref16 call timed out before final output; split instrumentation proved 4 panels at 49.5 seconds, and a fresh one-campaign ref1/2/4/8/16 execution exited zero with ref16 53.46 seconds. Preserve timeout and success separately.
- Local source/test/workflow/theory Git blobs were checked by exact SHA after publication. Installed-wheel GitHub CI result must be read from actual Actions run, not inferred from local pytest.
- Native Rust, general Bianchi II/V, tilted electron collisions, full polarized IQUV, arbitrary observational sky input, physical decimal acquisition, formal verification of MPFR/Python, and whole-repository tests: NOT_RUN or OUT_OF_SCOPE.

## Federation intake and provenance

Latest consulted: BASS PR238/239; BASS_HE PR104 (conditional daughter-energy stress trace), bass_cr PR119 (He cross-budget frontier), rec_bianchi PR154 (HD source-level enclosure), rei_bianchi PR260 (UVB conditional confidence union), WU088_HH PR155 (reactive HD source recovery, distinct owner), htt_base PR564 (report-first convergence). These are independent source-owner lanes and do **not** supply a physical collision rate to the present collisionless CE1-G channel. No cross-repo source/rate or science claim is silently promoted.

Primary literature: Ho Lee, Ernesto Nungesser, Paul Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen Rel Grav 52 (2020), DOI `10.1007/s10714-020-02699-7` (small-anisotropy asymptotics, different claim). Wu & Yang, *Error Estimation of Numerical Solvers for Linear Ordinary Differential Equations*, arXiv:1804.03363 (linear Hermite residual technique only). Exact BASS nonlinear comparison and tabulated-source contract are direct derivations, not quoted theorems from those papers.

## DAG/claim gate

Top-level 15 nodes/21 dependency edges unchanged, completed 9/15. CE-1 remains PARTIAL, CE1-G is a scoped subgate. R1–R10/C1–C10 stage ledger has 18 completed outputs and R6/C9 **distinct-author independent review NOT_RUN**. Production_ready=false; merge_ready=false; no main/parent/sibling branch mutation, no automatic next node. Next candidate CE1-H: independently verify MPFR software/derivative majorants or extend to a new physics channel only after explicit source contract; not executed here.
