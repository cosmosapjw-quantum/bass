# S9 VigilODE 새 결과·실제 API intake

이 intake는 새 S9 history 실행 전에 수행했다. VigilODE 전체 147개 branch를 두 페이지에서 확인했고, 최신 20개 PR과 최신 Actions 10개, 실제 Git tree 및 최신 게시 CSV를 읽었다. 관련 BASS·REI와 두 클라우드의 별도 intake가 완료되기 전에는 새 과학 캠페인을 시작하지 않았다. 세부 원본 식별자와 조회 범위는 `INTAKE.json`에 있다.

## 채택한 원본

| 종류 | 식별자 | 의미 |
|---|---|---|
| 저장소 | `cosmosapjw-quantum/vigilode` | 사용자가 지정한 실제 Rust 코드 |
| 기본 main | `8d0c79184e09efb5bdadc24a6315c60a71a44264` | 오래된 기본 branch여서 최신 구현으로 채택하지 않음 |
| 구현 원본 | `a21d573980f66fe02891bd216153443b5352f921` | `claude/nice-dijkstra-208xq0`, 2026-10-19 10:09:01 UTC |
| 원본 tree | `3eb56734d3dbde83298f6c96e33663b0ad0177b6` | 실제 tree SHA를 별도로 확인 |
| 최신 결과 게시 | Draft PR71, `ac1cd2a4738c2441c92e5fdae5f70aba35e53544` | `research/benchmark-results-20261019-dual`, 12:36 UTC |
| Run2 측정 구현 | `8a8bd409b1d96c7b7421f496d229e119fd3d284e` | 선택한 원본 및 최신 게시와 Rust 수치 구현 차이 없음 |

[PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)과 [고정 원본](https://github.com/cosmosapjw-quantum/vigilode/tree/a21d573980f66fe02891bd216153443b5352f921)을 직접 조사했다. 해당 원본의 전체 tree에서 `AGENTS.md`는 없었다. MIT license, 원본 Cargo manifest/lock, build script와 계수 fixture를 보존했다. 필요한 원본 178개 파일, 5,196,962 bytes의 SHA256 및 Git blob SHA1을 모두 검증했다. `VIGILODE_SOURCE.json`이 NCP에서 같은 파일만 받아 검증하는 manifest다.

## 새 게시 결과 반영

Run1 `endpoint_results.csv`는 154행 모두 completed/deterministic이며 보고된 endpoint WRMS와 경험적 reference spread의 합 최대가 0.9917799399710141이다. Run2 `ct_results_2700.csv`는 2,700 attempts 중 **2,639 ok / 54 refused / 7 solver_failure**였다. 성공 행 중 `R_up≤1`은 2,329개이고, `≤10`은 2,580개, `≤100`은 2,626개다. 원본 CSV bytes를 내려받아 Git blob과 SHA256을 독립 검증하고, 자체 CSV 집계 및 원본 `verify_csv.py`의 `PASS_SCOPED_CSV_INTEGRITY` 반환을 확인했다. 원래 solver benchmark는 다시 실행하지 않았다.

`fast-ctl-pi`의 해당 144개 적용 사례는 모두 ok 및 `R_up≤1`이었지만, 이것을 모든 문제 또는 BASS의 성공 보증으로 확대하지 않는다. `seq-mf-gmres`의 manufactured-vector-32 실패 6개는 inner-forcing norm의 비유한/음수 조건이고, 나머지 1개는 exponential fused driver의 attempt/step 실패다. 이번 adapter가 쓰는 실제 U-form `mf-fast` 경로에는 해당 inner-forcing 경로가 없다.

최신 Actions의 외부 workflow `success` 역시 benchmark pass로 읽지 않았다. strict 비교 Run39253322042가 보관한 내부 record는 `C2_RED`, test exit1, `benchmark_executed=false`였다. 10개 contract test 중 3개가 아직 구현되지 않은 admission 경로 때문에 실패했다. 오래된 process timing/allocation/Callgrind 요약은 최신 게시에 해당 raw 자료가 없어 `PRIOR_REPORT_ONLY`로 남겼다.

## BASS에 적용할 실제 기능

1. `integrate_rodas5p_mf_fast_observed_gmres_into_ls_workspace`를 사용한다. 실제 user JVP, identity mass, GMRES와 재사용 least-squares workspace가 있는 U-form RODAS5P 경로다. `faer 0.24.4`가 해당 선형대수 구현에 실제 사용된다.
2. `OdeProblem`에 analytic RHS/JVP와 **명시적 analytic partial_t**를 모두 제공한다. Ft callback을 빠뜨리면 upstream은 숨은 finite difference 경로를 사용하므로 생략하지 않는다.
3. 출력은 `OutputSchedule`의 정확한 requested stops를 사용한다. 최신 CSV에는 direct-grid와 dense 보간의 큰 차이가 실제로 있었으므로 dense 보간의 tolerance 성립을 가정하지 않는다.
4. 원래 `SmallProblem<N>` API는 time 인자가 없는 autonomous API다. 두 번째 arm은 실제 `[h,b,y,x]`, `x'=1`의 `SmallProblem<4>`와 analytic 4×4 Jacobian을 사용한다. 이는 3차원 MF와 오차 norm 차원도 다르므로 속도 우위나 동일 attempt 수를 주장하지 않는다.
5. 각 source birth에서 h,b,y는 연속이지만 RHS, Ft, Jacobian은 바뀐다. 이전 cohort를 그대로 보존한 새 immutable bank와 새 driver/workspace로 정확히 restart한다. reference에 저장된 b(u)는 비교에만 쓰고 실제 birth frame에는 현재 Rust 해의 b(u)를 사용한다.

## 전문 Rust 패키지와 검증

고정 VigilODE lock의 registry package 118개는 관련된 기존 offline archive에서 재사용했다. package checksum 및 내부 파일 checksum을 모두 확인했으며 총 67,334,526 bytes다. 추가 `num-rational 0.4.2`, `num-bigint 0.4.6`, `num-integer 0.1.46`은 기존 관련 vendor에서 743,303 bytes를 재사용했다. 새로 만든 native birth의 실제 binary64 입력에 대해 비정규화 `ΣαP2`, `ΣαP4`와 별도의 normalization을 정확한 `3/10^15`와 비교한다. 이 조건을 통과하기 전에는 cohort를 삽입하지 않는다. Python Fraction observer가 같은 raw 입력을 독립적으로 검산한다.

별도 reviewer는 `num-dual 0.15.1`을 development 검산에만 적용했다. 실제 컴파일한 analytic callback 190벡터 / 38 bank-state 점 / 5 bank와 독립 AD가 비교되었고, RHS 최대 1.409e-16, JVP 최대 4.285e-16, Ft 최대 8.523e-17의 scaled 차이였다. Ft 생략 및 birth 뒤의 stale Ft control은 거부되었다. 이 비교는 history를 실행하지 않았다. 상세 raw 결과는 `../theory_review/actual_callbacks/RESULT.json`에 있다.

첫 빌드는 minimal export에서 원본 integrator `build.rs`를 빠뜨린 탓에 compile-time profile 변수가 없어 exit101이었다. 실패 log를 보존하고 정확한 원본 build script를 추가한 후 실제 컴파일과 새로운 contract test 5개가 모두 통과했다. 기존 BASS owner와 upstream 수치 소스는 변경하지 않았다. 이 준비 성공은 아직 새 S9 과학 campaign 완료나 native finite-bin 보존의 승인이 아니다.

## 클라우드 새 결과 범위

관련 intake worker가 Dropbox `/ode_solver`의 Oct16 README/plan/dump와 `/VIGILODE_V35_BOOTSTRAP_IMPORT_20260819`의 5개 파일을 확인했다. Drive의 VigilODE 이름/폴더 검색에서 별도 최신 backup은 확인되지 않았고 PR71 backup도 발견되지 않았다. 따라서 최신 직접 실행 근거는 GitHub PR71의 raw CSV다. 이 범위 밖까지 클라우드에 새 결과가 없다고 주장하지 않는다. BASS/REI와 클라우드 전체 관련 조회 영수증은 root가 관리하는 별도 fresh-intake 기록에 있다.
