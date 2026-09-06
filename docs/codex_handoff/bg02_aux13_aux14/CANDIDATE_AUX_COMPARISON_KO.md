# BG02 — 기존 repaired candidate의 AUX 비교 및 Git-first 반환

상태: 다음 read-only 비교의 실행 인계. 미실행. 새로운 source 수리나 native17 승인이 아니다.

## 1. 완료된 선행 결과 — 재실행하지 않는다

주 대화는 historical control의 실제 source-subset AUX 결과를 검토했다. 실제 결과는 16 Success / 1 Failure / 미평가 0, process exit 1이며 유일한 Failure는 `AUX13_MOMENTUM_CONSUMER_SIGN`의 residual `2*C1`다. Driver/runtime 결함은 관측되지 않았다. 원본 FAIL_AUXILIARY를 유지한 채 제한된 HISTORICAL_CONFLICT_REPRODUCED 증거로 수용했다.

이 결과의 실행은 2026-09-06T14:03:16Z의 local run이다. 이후 Git-first 게시가 이를 재사용했다. 다른 날짜/폴더로 동일 원본 실행을 다시 하지 않는다.

Evidence publication: `892d8f33951a8d6bd7f785502a864c0f3688f162`
Evidence root: `artifacts/handback/bg02_aux13_aux14/20260906T144626Z/`

- [원본 final JSON](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/original/execution/aux-final-original.json)
- [실행된 원본 driver](https://github.com/cosmosapjw-quantum/bass/blob/892d8f33951a8d6bd7f785502a864c0f3688f162/artifacts/handback/bg02_aux13_aux14/20260906T144626Z/original/driver/BASS_AUX13_AUX14_V1.wls)
- [주 대화 과학 검토](../../research/bg02_aux13_aux14/SCIENCE_REVIEW_20260907_KO.md)

마지막 상대 링크의 기준은 저장소 docs 디렉터리다. 찾을 때에는 정확한 저장소 경로 `docs/research/bg02_aux13_aux14/SCIENCE_REVIEW_20260907_KO.md`를 사용한다.

## 2. 이번 목표와 로컬이 필요한 이유

```text
ROLE=LOCAL_HOST_EXECUTOR_AND_BOUNDED_REPAIR
TASK=BG02_REPAIRED_CANDIDATE_AUX13_AUX14_COMPARISON
SEPARATE_WORK_THREAD=NOT_USED
REPOSITORY=cosmosapjw-quantum/bass
```

주 대화에서 현재 GitHub 경로로 아래 candidate commit을 읽으려 했지만 404였다. 로컬에 이미 존재하는 candidate의 실제 files/object와 installed Wolfram kernel만 이 작업에 필요하다. 새 scientific candidate를 만들지 말고 기존 것을 읽는다.

```text
CANDIDATE_COMMIT=e404f914c0817b4c2ab3a0ff4632a8457e026fde
CANDIDATE_DIRECT_PARENT=3c36458a8dbc9fe4092a24d5a09203327877f8d8
CANDIDATE_TREE=e2fc64860631e781082cceb3bef5b24fb8a06084
HISTORICAL_CONTROL=f2f05d37cdc6476154869067b1d41436af8248b6
ORIGINAL_DRIVER_GIT_BLOB=8255b580026bd44ead4798c5e8d2be4367495261
ORIGINAL_DRIVER_SHA256=5f80ed5d691bdf4466b60920ce98029ea092666c3831b7998b4787eb8e80c516
```

실제 candidate 객체/기존 bundle/검증된 복원물과 현재 동일 candidate 실행이 있는지 먼저 확인한다. 존재하는 같은 비교 결과를 재사용한다. 후보를 얻지 못하면 정확한 missing-source 상태와 확보된 파일만 반환한다. 다른 최신 branch나 historical source에 한 줄 sign patch를 넣어 이 candidate라고 가장하지 않는다. Hash는 source 구분이며 새로운 임의의 scientific gate가 아니다.

## 3. Source 비교를 먼저 하고 같은 suite를 실행

기존 candidate의 scientific source는 read-only로 둔다. 작업 중인 dirty checkout을 건드리지 말고 읽기 전용 snapshot 또는 별도 복원 경로를 사용한다. 실제 commit/parent/tree 또는 복원 방식 및 각 파일 identity를 기록한다.

먼저 original four source의 candidate 버전과 필요한 loader/owner dependency를 읽는다. `EinsteinProjection.wl`의 MomentumProjection이 실제로 `-DivergenceK+GradientK-kappa_G*qComponent`를 의미하는지, convention owner가 무엇인지, 기존 geometry generator와 배열 adapter를 재사용하는지 확인하고 source 차이를 반환한다. 사라진 import나 새로운 필수 dependency를 stub/no-op으로 대체하지 않는다.

그 다음 게시된 동일 원본 driver로 candidate의 기존 API를 호출한다. source subset을 사용하면 required dependency closure도 명시하고 source-subset replay라고 쓴다. 전체 checkout의 파일 존재가 전체 tree의 모든 code path 실행을 뜻하지 않는다.

원본의 17개 TestID·물리 입력·기대값·expected-message 의미는 고정한다. 이번 비교의 기대는 candidate에서 17 Success / 0 Failure지만 이는 관측 전 예측이다. Historical 결과 16/1/exit1과 candidate 실제 결과를 독립 표로 반환한다. 수리된 candidate의 결과를 historical 기록 위에 덮어쓰지 않는다.

기존 local Wolfram kernel을 `wolframscript -local <actual kernel> -file <driver>`로 직접 호출한다. 기존 per-process inner 120초 / outer 150초 / TERM 후 10초 kill 및 실제 존재하는 총자원 상한을 유지한다. Source loader에 필요한 기존 dependency는 정상적으로 소비하되 xAct 설치/교체나 native calibration suite 실행을 추가하지 않는다. 새 설치·라이선스·영구 runtime 설정 변경은 이 범위 밖이다.

## 4. 범위 내 자동 수리와 불변 경계

재현된 실행 경로·argv·current-process 환경·loader context·driver API/결과 수집/종료코드·반환 패키징 결함은 같은 목적 안에서 자율 수정하고 관련 회귀 및 원래 target을 재검증한다. Original driver와 첫 결과를 먼저 보존하고 repair revision을 분리한다. 각 재실행에는 실제 수정 또는 새로운 진단 근거가 있어야 한다. 동일 실패를 의미 없이 반복하지 않으며 한 번 편집했다는 이유로 종료하지 않는다.

이번 task는 **기존 candidate의 read-only 비교**다. Candidate scientific source/owner registry/보호된 물리 의미의 수정, 원래 expected residual 변경, 새로운 physics나 AUX15는 하지 않는다. 추가 비영점이 plumbing 때문인지 진단한 뒤 실제 candidate source 수정이 필요하면 원본 관측과 최소 patch 제안을 반환한다. Source 수리 자체의 다음 범위를 주 대화가 결정한다.

기존 capture-six/native17, owner WLT6, 이전 7파일 capture 수리 또는 별도 native gate를 실행하지 않는다. 해당 suite의 실패를 이 보조 비교가 해결한 것으로 쓰거나 소모된 예산을 갱신하지 않는다.

주의: 기존 테스트는 GradientK=0, scalar consumer에 test-supplied norm, driver-supplied Jacobi rates를 사용한다. 따라서 17/17이 나와도 일반 gradient 항·state ingestion·production Jacobi RHS·generic native 4-projection bridge·time-integrated stability까지 검증됐다고 쓰지 않는다. 주 대화의 새 h 보존/clamp 반례 유도는 이번 frozen suite에 몰래 추가하지 않는다.

## 5. 원격 반환 — 파일 수동 이동 없음

기존 Git-first/R2 원칙을 유지한다. 격리된 이 비교 전용 evidence branch에 아래를 읽을 수 있는 파일로 commit/non-force push한다. 원본 scientific branch와 historical evidence는 그대로 둔다. Merge/force push/workflow 수정/수동 CI dispatch는 하지 않는다.

- `CHATGPT_HANDOFF_KO.md`: actual candidate intake, source 차이, actual 결과, 수리 여부, 남은 boundary.
- `RETURN_STATUS.json`: 두 source의 identity, original/repair 구분, exact ID별 결과, 명령·actual exit·시간·runtime failure·messages, 재사용/신규 구분.
- 실제 original/repair stdout/stderr, final JSON, driver 및 재현된 harness patch/회귀시험.
- Candidate scientific source의 필요한 읽기 가능한 사본 또는 정확히 게시되어 접근 가능한 canonical file 링크, dependency 정보, historical-to-candidate source diff. 후보 전체 vendor/archive를 중첩 복제하지 않는다.

핵심 결과를 ZIP에만 넣지 않는다. 실제 remote ref와 handoff/결과/관련 source 본문을 다시 읽고 publication commit/tree, HANDOFF_URL, RESULT_URL을 최종 출력한다. Execution source와 publication commit은 분리한다. 게시만 실패하면 과학 계산을 다시 돌리지 않고 PUBLICATION_BLOCKED를 따로 반환한다.

수용 가능한 비교 결과를 얻으면 반복 review를 만들지 말고 바로 반환한다. 실패/차단된 경우에도 실제 확보한 증거와 정확한 blocker를 게시한다. 사용자에게 다운로드/재업로드를 요구하는 방식은 정상 경로가 아니다.
