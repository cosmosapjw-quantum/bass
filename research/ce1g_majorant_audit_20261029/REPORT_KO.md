# CE1-G 독립 R6/C9 감사와 positive-ray derivative majorant 수리

## 1. 실제 과학 상태

- **선택 단위:** CE1-G의 양의 ray source와 MPFR whole-panel 시간오차 보증에 대한 bounded independent math/code audit 및 한 건의 증명전제 수리.
- **부모:** cosmosapjw-quantum/bass Draft PR #240, 원본 HEAD `0fd95e4baadf8982cdb1f9f81725b7b8e8fd0aa1`, CE1-F 기준 PR #239. 부모의 완전한 85-member ZIP(15,527,023 bytes, SHA256 `8657f6e7ad51b516896c0a9988644b12790b6cdc48372e14945f8232c4942448`)은 수정하지 않았다.
- **현 상태:** 발견한 `_ce1c_stored_mass_cap` 캐시의 보증 전제를 고쳤으며, 변경되지 않은 부모 고정 자료의 scoped 결과는 유지됐다. 상위 CE-1은 `PARTIAL`, 15개 노드/21개 edges 중 scoped 집계 **9/15**, `production_ready=false`, `merge_ready=false`.
- **물리:** (-,+,+,+), normal proper u=t/Tstar, h_i=Tstar H_i, E,P_i=(8πG Tstar²/c²)*(physical energy/pressure), Lambda0, 대각·반사대칭·양의 조각상수 angular table의 무질량 무충돌 Bianchi I, 전 방향 팽창. MPFR192 RNDD/RNDU; 임의의 관측 하늘지도·충돌·tilt·공간 EFE·native 코드는 범위 밖.

## 2. 독립 발견: 변경된 source를 이전 캐시로 검사할 수 없다

기존 `einstein_interval.stored_ray_energy_majorant()`는 source 객체에 `_ce1c_stored_mass_cap`을 저장했다가 다음 호출에서 무조건 반환했다. 그러나 CE1-G의 공개 검증 경로는 `s.mass=s.mass.copy()*1.2` 식의 양의 source 대체를 허용한다. 이전 Ray/mass 기준 상계를 이후 양의 source에 재사용하면 4차 미분 residual의 upper bound 자체를 과소평가할 수 있다.

실제 독립 Python3.13.5 재현 (6개 ray, 4개 RK4 panels, 첫 panel): 첫 mass cap 0.9, source.mass 100배 수정 뒤 과거 helper는 0.9를 재사용하지만 현재 값으로 계산해야 하는 cap은 90.0이다. 수정 전 4차 미분 upper 2377.899825988017; 질량 100배의 적절한 upper 213074.8769262066이다. CE1-G의 time residual 전체에서 `R4 h^4/24`의 누락 가능성을 수학적으로 명시한다. 원래 CE1-G 고정된 1536-ray 계산의 결론이 거짓이라는 반례는 아니다.

## 3. 4차 미분 상계의 수학적 구조

양의 stored ray q와 mass w에 대해, source의 한 성분은

`p_i(u)=w n_i² exp(-sum_j ell_j(u)-2ell_i(u)) [sum_j n_j² exp(-2ell_j(u))]^(-1/2)`.

`ell_j`는 한 Hermite panel에서 3차 실수 다항식이다. 지수함수와 역제곱근의 4차 미분에 product rule 및 Faà di Bruno 형식의 양의 계수 주요항을 사용하면 `|p_i^(4)|<=p_i F(H1,H2,H3)`이며 F는 비음수 다항식이다. 전 방향 팽창 `ell_j>=0`와 `w>0`에 대해 `p_i<=w||n||`이므로 모든 ray의 합은 `Ecap F`, `Ecap <= (sum_j w_j) max_j ||n_j||`로 상계할 수 있다. 이 `Ecap`은 반드시 **현재 stored mass/ray의 정확한 binary 값**으로부터 얻어야 한다.

SymPy 독립 계산에서 `D^4 exp(g)/exp(g)`와 `D^4 Z^(-1/2)/Z^(-1/2)`의 계수 항등식은 모두 잔차 0을 기록했다. 증명 전제 수정은 이 derivative formula를 바꾸지 않는다.

## 4. 최소 구현·TDD 결과

`einstein_interval.py`의 `stored_ray_energy_majorant()`에서 *unkeyed cache reading/writing*만 제거하고, 기존 `exact_component_sum`·정확한 Fraction ray norm·MPFR outward 산술은 그대로 사용한다. 기존 Einstein/Vlasov RHS, Hermite 다항식, 적분기, 물리 입력, 일치 허용오차, CE1-G source/time 비교식은 변경하지 않았다. Cache-hit 성능을 포기하지만 ray 384개 fixture의 실제 비교는 약 9초이며, source가 변경된 상황의 거짓 upper bound보다 안전을 우선했다. Ref16 벤치마크 성능은 새로 측정하지 않았다.

신규 4개 테스트를 먼저 실행했을 때 **3 FAIL, 1 PASS**, 수정 후 **4 PASS**. 변경과 관련된 CE1-G 및 이전 CE1-A/B/C/D/E/F 회귀 테스트를 합쳐 **76 PASS**. 실제 실행한 명령은 다음과 같다:

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/nonperturbative/test_ce1g_positive_ray_majorant_mutation.py tests/nonperturbative/test_einstein_tabulated_time.py tests/nonperturbative/test_einstein_tabulated_source.py tests/nonperturbative/test_einstein_exponential_source.py tests/nonperturbative/test_einstein_physical_input.py tests/nonperturbative/test_einstein_interval.py tests/nonperturbative/test_einstein_error_budget.py`

Current GitHub Actions scoped run `40805976099` succeeded: 76 tests PASS, pinned ref8 fixed-source source/time/total selected output fields EXACT match, installed wheel source mutation check PASS. `set -euo pipefail` enabled; no false-success pipeline.

**부모의 고정된 refinement 8:** source upper 0.00014304386431693807, total h upper 1.2322918653868093e-5, time+jump h 8.354157831006931e-7, max h knot jump 6.938893903907228e-18. 부모 보존 파일과 선택한 필드가 정확히 일치했다. Ref16 원래 목표 `3.7019164499698285e-6<1e-5`는 원본 evidence를 보존했으며 이번에는 긴 과학 캠페인을 재실행하지 않았다.

## 5. 감사·공개·보존의 경계

이번 작업의 R6/C9는 새 자료를 읽고 실제 반례를 독립적으로 재현하여 과학/코드 결함을 수정한 **scoped method review**다. Native subagent 또는 다른 연구자에 의한 `distinct-author R6/C9`는 여전히 NOT_RUN이다. 전체 Python/MPFR 소프트웨어의 형식검증, multiprocessing source mutation 동시성, 실제 부동소수점 환경·compilers의 검증은 이번 결과가 아니다.

원래 CE1-G Archive는 Google Drive에서 전체 SHA256 확인하고 Dropbox에 create-only 추가 업로드하여 이전 `NOT_DONE` 상태를 실제 성공으로 바꾸었다. 본 S0/S1 및 최종 S2도 Git+Drive+Dropbox 경로별 확인 수준을 명시한다. 모든 원본 PR #239/#240, CE1-F PR #238/#241, main/owner는 수정하거나 merge하지 않았다.

## 6. 그 다음의 과학

현재 상위 CE-1은 여전히 `PARTIAL`, 9/15 유지. CE1-H는 일반 관측 테이블의 입력 불확실성 또는 실제 Python/MPFR/Rust 경계의 독립 형식검증 중 하나를 선택하되, CE1-G의 이미 인증된 고정 입력 결과를 무의미하게 재실행하지 않는다. 다음 스레드는 이 독립 repair PR을 `merge_ready=true`라고 자동 판정하지 말고 기존 정책 RF-00/RF-BENCH 오픈 이슈와 source authority PR239를 함께 검토한다.
