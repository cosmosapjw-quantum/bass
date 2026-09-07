# BG02 conditional abstract projection contraction — 실행 반환

TASK=BG02_ABSTRACT_CURVATURE_BLOCK_CONTRACTION_V1
STATUS=PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY

실제 설치된 Wolfram/xTensor로 원래 AP00–AP12를 실행하고, 새 코드의 API 사용·결과 캡처 결함을 교정했다. 최종 repair3은 **13 Success / 0 Failure / 0 unevaluated / actual exit 0**, whole-invocation messages `[]`, runtime failures `{}`, stderr 0 bytes다. 이는 Gauss/Codazzi/normal-Ricci 블록을 전제로 한 조건부 abstract contraction 결과이며, arbitrary metric/commutator에서 블록 자체를 유도한 증거는 아니다.

## 정확한 소스와 실행 경로

- Repo: cosmosapjw-quantum/bass
- Branch: `evidence/bg02-abstract-projection-20260907T114615Z`
- Delivery commit/tree: `e7377375ec6d42474ed559acdf48ecbe8a26723b` / `9a31a699a30b269fef9e947bfaf14fd655411a47`
- Tested AP code commit/tree: `4149649462758165e64673ebb86498b708ef9a0e` / `0e67bbfa439fd249a9d69136c60e52b6357066d5`
- Dependency candidate: `e404f914c0817b4c2ab3a0ff4632a8457e026fde`, tree `e2fc64860631e781082cceb3bef5b24fb8a06084`.
- 원본 source-subset publication: `2e1b6e2f12cc766c8ffe1160d6371a88730064a8`.
- Runtime BASS_REPO는 checkout의 `artifacts/handback/bg02_repaired_aux_comparison/20260907T052727Z/source/`다. delivery의 historical root kernel을 소비하지 않았다.
- 여섯 파일 Git blob 및 모든 실행의 host before/after SHA256을 보존했다. 실제 Get은 BG02Convention.wl과 EinsteinProjection.wl이고 owner가 JSON을 읽는다. 세 geometry 파일은 hash 확인만 했으며 실행하지 않았다.
- 실제 runtime: `/usr/bin/wolframscript -local /usr/local/Wolfram/WolframEngine/15.0/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel -file <runner>`; inner180, external timeout240, TERM 후 kill10초.
- Wolfram: `15.0.0 for Linux x86 (64-bit) (May 26, 2026)`; xTensor: `{"1.3.0", {2025, 12, 29}}`.
- xTensor init: `/home/cosmosapjw/.WolframEngine/Applications/xAct/xTensor/Kernel/init.m`; SHA256 `de9dc682f479e05d3fca377a15036c823023fa444f3456603317fc0fd8e2b1a0`. init 전후 일치이며 전체 package archive seal을 검증했다고 주장하지 않는다. 설치·업그레이드·license·영구 환경 변경 없음.

## 첫 실패와 교정

| AP 대상 실행 | 실제 exit | 관측 AP rows | 분류 |
|---|---:|---:|---|
| original | 0 | 0 | Validate::inhom, stderr Throw::nocatch, final JSON 없음; 13개 미평가 |
| repair1 | 2 | 0 | Validate::repeated를 최종 AP_INVALID_RESULT에 보존; 13개 미평가 |
| repair2 | 2 | 0 | 반복문 규칙의 바인딩 수정 후 남은 하첨자 충돌; 13개 미평가 |
| repair3 | 0 | 13 | 13 Success, 메시지/runtime failure 없음 |

원본 exit0은 수학적 성공이 아니다. original/repair1/repair2에서 AP assertion이 13개 실패한 것도 아니다. 모두 TestReport 이전 구현 오류이며 required ID별 UNEVALUATED는 `AP_OUTCOMES_ALL_ATTEMPTS.json`에 구분했다.

수정은 두 새 파일의 14 insertions / 11 deletions다. `projection_tests.wl`과 물리 기대식·고정 BASS 의존성은 byte-identical이다.

1. xTensor MakeRule은 첫 인자를 보류한다. helper projector/trace RHS와 Table iterator의 tensor head를 먼저 Evaluate해 실제 free indices 및 직교성/STF 규칙을 생성했다. 새 물리 전제를 추가하거나 target residual을 0으로 rewrite하지 않았다.
2. ReplaceIndex는 상·하첨자 규칙을 별도로 취급한다. 실제 computed M/S의 free lower slots `-ia`, `-ib`를 치환하고, 그 전에 dummy를 freshen하도록 했다. expected projection을 재구성 입력으로 넣지 않았다.
3. runner의 apMain을 Catch로 감싸 native untagged Throw가 무기록 exit0으로 끝나지 않게 했다. 오류 메시지는 Quiet 처리하지 않고 그대로 stdout/final JSON에 유지한다.

원본 파일은 `original_code/`, 모든 AP revision은 `execution/<attempt>/code/`, patch는 `repair.patch`에 있다. 진단 3개와 원시 실패도 별도로 보존했다.

## 실제 검증 결과

- AP00_XTENSOR_RICCI_CONTRACTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP01_CURVATURE_SYMMETRIES: Success; actual `HoldForm[{0, 0, 0, 0}]`, expected `HoldForm[{0, 0, 0, 0}]`.
- AP02_GAUSS_BLOCK: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP03_CODAZZI_BLOCK: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP04_NORMAL_RICCI_BLOCK: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP05_HAMILTONIAN_PROJECTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP06_MOMENTUM_PROJECTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP07_SPATIAL_TRACE_PROJECTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP08_SPATIAL_PSTF_PROJECTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP09_FULL_RESIDUAL_RECONSTRUCTION: Success; actual `HoldForm[0]`, expected `HoldForm[0]`.
- AP10_EXISTING_CONSUMER_ADAPTER: Success; actual `HoldForm[{0, 0, 0, 0}]`, expected `HoldForm[{0, 0, 0, 0}]`.
- AP11_LIE_METRIC_TRACE_ADAPTER: Success; actual `HoldForm[{0, 0}]`, expected `HoldForm[{0, 0}]`.
- AP12_TRACE_MUTATION_NONZERO_WITNESS: Success; actual `HoldForm[{0, 0}]`, expected `HoldForm[{0, 0}]`.

각 row의 actual/expected messages와 raw TestEvaluated 이벤트는 최종 JSON/stdout에 있다. expected_messages의 `HoldForm[{}]`는 TestReport 직렬화이고 actual_messages는 `{}`다. Host readback helper가 처음 두 문자열을 혼동한 검사를 고쳤으며 AP 결과·코드·기대값을 변경하거나 Wolfram을 재실행하지 않았다.

- AP00: 실제 xTensor Riemann-to-Ricci contraction 0. convention을 뒤집지 않았다.
- AP01: algebraic curvature symmetry 네 잔차 0.
- AP02–AP04: 입력한 세 곡률 블록 회복 0. 전제 자체의 독립 differential proof가 아니다.
- AP05–AP09: 계산된 네 projection과 전체 E 재구성 0. generic DK, nonzero acceleration, matter q/pi를 유지했다.
- AP10: pinned BASS consumer 네 비교 0. SpatialPSTFProjection의 SigmaQuadratic에 (K.K)_PSTF를 공급하며 ShearLieRate는 호출하지 않는다.
- AP11: LieDToCovD로 inverse-projector Lie identity와 contracted trace correction을 실제 계산, 두 잔차 0.
- AP12: computed bad-minus-good는 `4 HH[]^2 + (4/3) Sigma_ab Sigma^ab`, 실제 fixed-reference witness `4`. expected4를 hand-entered 관측값으로 대체하지 않았다.

실제 projection/trace 표현식은 `COMPUTED_PROJECTIONS.md`와 raw final JSON에 있다. abstract exact algebra이므로 새 기대값 plot을 만들지 않았다. SC19/19, shape5/5, 기존 실제 SC 그림과 AUX 결과는 이전 범위에서 재사용했으며 새 실행으로 세지 않았다.

## 작은 회귀 검사와 비용

`native_api_regressions.wls`는 위 API defect의 원본/수정 형태를 검사한다. 완성된 같은 스크립트 RED2는 6 Failure / 2 Success / exit1, GREEN2는 8 Success / exit0이다. 최초 regression-red 자체는 의도된 원본 오류를 비교식에서 Catch하지 못해 report 이전 종료했고 그 원시 증거도 보존했다. 그 캡처 helper를 고친 후 같은 스크립트를 RED/GREEN으로 실행했다. 이전 GREEN의 8/8도 별도로 보존했다.

실제 repaired runner의 isolated Throw fixture는 final AP_INVALID_RESULT와 actual exit2를 내서 실패 캡처 동작을 검증했다. 이것은 새로운 AP 물리 실패가 아니라 의도한 invalid-result regression이다.

AP target4 + 진단3 + regression5 = Wolfram process12, 누적 실제 wall 107.206885초, 최장 23.347837초. timeout 없음. 자식/로컬 LLM 호출0, SC/AUX/native17/capture6/ownerWLT6 호출0. 상세 argv·시각·exit·원시 stdout/stderr·hash는 `ATTEMPT_ACCOUNTING.json` 및 execution에 있다.

## 갱신된 전역 하네스와 반환 경계

실제 설치 authority `02ceeb6dc2e0568cefede48b6f9928799e61ac74`의 AGENTS/GLOBAL_EXECUTION_POLICY/local-router를 읽었다. 사용자 지정 LOCAL_HOST_EXECUTOR_AND_BOUNDED_REPAIR와 SEPARATE_WORK_THREAD=NOT_USED에 따라 HOST_CODEX_ONLY를 사용했다. CODEX_ONLY/BUDGET_FIRST를 별도로 선택하지 않았고 하위 모델 호출로 policy 활성화를 시험하지 않았다. 한 coherent repair episode 안에서 관측 오류에 따른 세 revision을 유지했다. 부모의 검토는 같은 작성자의 검토이며 독립 리뷰라고 주장하지 않는다.

`[skip ci]` code/evidence commits를 AP 전용 branch에 non-force 게시한다. main, PR131 historical head, candidate source 및 기존 evidence refs는 보존한다. Actions/CI/workflow/merge/force push 없음. publication commit/tree는 실제 최종 반환의 immutable HANDOFF_URL/RESULT_URL에 결합된다. publication-only readback 문제가 생겨도 수학 실행을 다시 하지 않는다.

NOT_VERIFIED: curvature-definition-to-blocks derivation, general-native BG02/native17 completion, finite-time/background evolution or numerical stability, arbitrary-family readiness, provider/RF04/production admission, entire xTensor archive seal. 성공 ceiling은 PASS_CONDITIONAL_ABSTRACT_CONTRACTION_ONLY다.

NEXT: 이 조건부 contraction 결과를 주 대화에 반환한다. curvature definition에서 blocks까지의 native 유도는 별도의 owner-scoped 과제다.
