# BG02 기존 repaired candidate AUX 비교 반환

STATUS: `COMPLETED_READ_ONLY_CANDIDATE_AUX_COMPARISON`
판정: `PASS_AUXILIARY_ONLY`; 전체 native/scientific admission은 하지 않는다.

기존 candidate `e404f914c0817b4c2ab3a0ff4632a8457e026fde`를 실제 로컬 Git
객체/clean checkout에서 확보했다. 직계 parent는
`3c36458a8dbc9fe4092a24d5a09203327877f8d8`, tree는
`e2fc64860631e781082cceb3bef5b24fb8a06084`로 요청과 일치한다.
다른 branch나 sign patch로 candidate를 재구성하지 않았다. 기존 기록을
검색했지만 동일 candidate의 AUX 비교는 없었고, 새로 실행했다.

| 대상 | 재사용/신규 | Success | Failure | 미평가 | actual exit | elapsed s |
|---|---|---:|---:|---:|---:|---:|
| Historical f2f05d37, 원본 driver | 2026-09-06 실행 재사용 | 16 | 1 | 0 | 1 | 3.608720 |
| Candidate e404f914, 원본 driver | 신규 original | 0 | 0 | 17 | 2 | 5.512157 |
| Candidate e404f914, loader repair1 | 신규 repair1 | 17 | 0 | 0 | 0 | 4.366319 |

Historical raw `FAIL_AUXILIARY`와 유일한 AUX13_MOMENTUM_CONSUMER_SIGN의
`2*C1` residual은 그대로다. Historical의 실행 시각은
`2026-09-06T14:03:16.742099+00:00`이며 이번에 재실행하지 않았다.
[기존 publication](https://github.com/cosmosapjw-quantum/bass/tree/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z)의 기록을 재사용했다.

Candidate original은 `2026-09-07T05:30:30.773874+00:00`에 실행되어
`BLOCKED_RICCI_NOT_EVALUATED`로 종료했다. 원본 driver가 candidate의 새
`Authority/BG02Convention.wl` dependency를 로드하지 않아 Ricci가 평가되지
않았다. TestReport 자체가 시작되지 않았으므로 17개의 수학적 실패로 세지
않으며 RuntimeFailures와 per-test messages는 미관측(null)이다.

기존 dependency 한 개를 원래 loader 순서대로 추가한 별도 repair1 driver로
`2026-09-07T05:32:25.046547+00:00`부터 `2026-09-07T05:32:29.413943+00:00`까지 실행했다.
17개 required/observed ID와 17개 TestEvaluated 사건이 정확히 일치한다.
모든 actual_messages는 `{}`, expected_messages는 `HoldForm[{}]`,
RuntimeFailures는 `{}`, stderr는 0 bytes이며 timeout이 없다.

과학 소스/owner registry는 0개 수정했다. 실제 실행에 쓰인 여섯 파일을 exact
commit에서 별도 read-only source snapshot으로 추출했다. 변경한 driver bytes는
Get 목록의 owner-module 한 항목뿐이며 TestID, 물리 입력, 기대값,
expected-message 의미와 종료 코드 로직을 보존했다. 해당 loader 회귀 2개는
원본에서 1 failure, repair1에서 2 pass다. 원본/repair driver와 첫 raw 결과,
patch, 회귀 로그를 모두 분리해 보존했다.

소스 읽기 결과 MomentumProjection은 owner 계수 `{-1,1,-1}`를 통해 실제로
`-DivergenceK+GradientK-kappa_G*qComponent`를 의미한다. Owner는 `bass`의
`BASS_BG02_OWNER_CONVENTION_V2`다. 기존 geometry generator와 배열 adapter를
재사용하며, 이 부호/typed-curvature 변경은 direct parent R1에서 상속되었다.
자세한 함수·dependency·historical diff는 [SOURCE_COMPARISON.md](SOURCE_COMPARISON.md),
[읽을 수 있는 source](source/), [exact diff](source-diff.patch)에 있다.

| TestID | Historical (reused) | Candidate repair1 |
|---|---|---|
| AUX13_CLASS_B_DIVERGENCE | Success | Success |
| AUX13_STORAGE_ORDER_PARITY | Success | Success |
| AUX13_ISOTROPIC_DIVERGENCE | Success | Success |
| AUX13_EXCEPTIONAL_DETERMINANT | Success | Success |
| AUX13_FULL_MOMENTUM_WITNESS | Success | Success |
| AUX13_SHEAR_NORM_SURVIVAL | Success | Success |
| AUX13_HAMILTONIAN_CONSUMER_SURVIVAL | Success | Success |
| AUX13_MOMENTUM_CONSUMER_SIGN | Failure (2*C1) | Success |
| AUX14_SPATIAL_RICCI | Success | Success |
| AUX14_NONZERO_HAMILTONIAN | Success | Success |
| AUX14_ACTUAL_RATE_VALUES | Success | Success |
| AUX14_JACOBI_VECTOR_DERIVATIVE | Success | Success |
| AUX14_CURVATURE_DERIVATIVE | Success | Success |
| AUX14_SHEAR_NORM_DERIVATIVE | Success | Success |
| AUX14_DIRECT_HAMILTONIAN_DERIVATIVE | Success | Success |
| AUX14_PROPAGATION_RATE_SEPARATION | Success | Success |
| AUX14_FERMI_ALIGNMENT_COUNTEREXAMPLE | Success | Success |

실행은 기존 Wolfram 15.0.0 kernel을 `wolframscript -local <actual kernel>
-file <driver>`로 직접 호출했다. inner 120초, outer 150초, TERM 후 10초 kill을
유지했고 기존 process/cgroup 자원 제한을 그대로 상속했다. 관측된 memory/cpu
cap이 unlimited인 곳에 임의의 총자원 상한을 주장하지 않았다. 정확한 argv,
cwd, current-process environment override, UTC 시각, exit와 시간은 각
[original process](execution/original/process.json)와
[repair1 process](execution/repair1/process.json)에 있다.

이번 결과는 **required dependency closure를 포함한 source-subset replay**다.
Candidate 전체 tree가 존재한다는 사실은 전체 code path의 실행을 뜻하지 않는다.
GradientK=0 검사이며 scalar norm은 test-supplied, aDot/nDot 및 curvature
derivative는 driver-supplied다. 일반 gradient, production state ingestion,
production Jacobi RHS, generic native 4-projection bridge, time-integrated
stability까지 확장하지 않는다. 새 h/clamp 반례나 AUX15를 추가하지 않았다.
Capture6/native17/owner WLT6 호출은 각각 0회이고 그 과거 실패/예산도 유지했다.
xAct 설치·교체, 라이선스·영구 runtime 설정 변경은 없다.

원본 작업 checkout과 기존 candidate checkout은 그대로다. 게시 branch는
`evidence/bg02-repaired-aux-comparison-20260907T052727Z`이며 scientific branch, historical evidence, workflow를 수정하지
않는다. Execution source와 이 evidence의 publication commit은 구분한다.
이 파일을 포함하는 Git commit이 publication identity이며 remote ref와 본문을
확인한 exact commit/tree 및 HANDOFF_URL/RESULT_URL은 최종 반환에 둔다.

검증 범위 내 비교가 완료되어 추가 scientific 실행이나 반복 review 없이 반환한다.
이는 Host의 source/raw-result 검토이며 independent reviewer PASS라고 쓰지 않는다.
