# BASS 주 대화–Local Codex Git-first 인계·반환 — R3

문서 상태: 실행·공유 계약. 이 문서의 게시 자체는 AUX 실행, 수정 완료, native 검증 또는 과학적 수용의 증거가 아니다.
권위: 2026-09-06 현재 주 대화의 사용자 지시. 인계·반환 파일은 가능한 한 GitHub에 commit/non-force push하여, 사용자가 다운로드·재업로드하지 않고 Codex 출력이나 링크만 전달한다.

## 1. 읽기 순서와 이번 개정

1. 이 파일: Git-first 공유와 한정된 게시 권한.
2. R2 자동 수리·반환 계약 전체: https://github.com/cosmosapjw-quantum/bass/pull/131#issuecomment-5559764991
3. 원본 AUX13/AUX14 driver·17 TestID·기대값 전체: https://github.com/cosmosapjw-quantum/bass/pull/131#issuecomment-5558019655
4. 이전 source intake·로컬 직접 실행 설명: https://github.com/cosmosapjw-quantum/bass/pull/131#issuecomment-5558745032

이 파일은 과거 인계의 일반적인 `push 금지`, `로컬 ZIP을 사용자가 다시 업로드`, `댓글만으로 handoff 전달`을 인계·반환 자료의 한정된 원격 게시에 대해서만 대체한다. 물리 source 변경 범위를 늘리지 않는다. R2의 근거 기반 자동 수리 권한은 유지한다. 과거의 `한 번 실행 후 무조건 중단/수리 금지`를 되살리지 않는다.

주 대화에서 가능한 연구·유도·코딩·검증은 주 대화가 담당한다. Local Codex는 실제 host 기능이 필요한 실행과 그 실행에서 드러난 범위 내 문제의 수리·검증·반환을 담당한다. 별도 work 스레드는 기본 경로가 아니다. 인계 파일 생성은 자동 Codex dispatch가 아니다.

## 2. 현재 실행 task와 불변 범위

```text
ROLE=LOCAL_HOST_EXECUTOR_AND_BOUNDED_REPAIR
TASK=BG02_AUX13_AUX14_ACTUAL_CONSUMER_VALIDATION
CONTROL_AUTHORITY=MAIN_CHATGPT_CONVERSATION
SEPARATE_WORK_THREAD=NOT_USED
REPOSITORY=cosmosapjw-quantum/bass
HISTORICAL_CONTROL_COMMIT=f2f05d37cdc6476154869067b1d41436af8248b6
HISTORICAL_CONTROL_TREE=8a1d6fbb0c039fe7bd0e29f79cb4e581e4b70688
```

문서가 담긴 publication commit을 실제 execution commit으로 사용하지 않는다. 위 historical control의 네 scientific source가 검사 대상이다. 네 파일만 복원하면 source-subset replay이며 full checkout/native replay가 아니다.

`wolfram/BASS/Kernel/` 아래 고정 입력:

| 경로 | Git blob |
|---|---|
| Geometry/StructureConstants.wl | d224da1091da815d3979bdc3262ca65b4ab83ee4 |
| Geometry/LeviCivitaConnection.wl | c8e4be28b00956b1fe2009a7d5bc8222a45585e0 |
| Geometry/ONFConnectionCurvature.wl | 820d09dd2bb0c5364b0fe3c0d0bdb3bc7841bb7c |
| Background/EinsteinProjection.wl | c7d40bd046b69fb9d1715538cfc7d570efc5e791 |

기존 matching run/return을 먼저 읽고 재사용한다. 없다면 기존 Git 객체 또는 인증된 GitHub read로 위 파일을 취득한다. 원본 driver는 지정 댓글의 Wolfram 코드 블록에서 자동 추출하고, 원문 댓글과 실제 추출 파일 identity를 보존한다. 사용자가 코드 블록을 손으로 옮기게 하지 않는다.

이전 반환 ZIP이 실제 존재할 때만 보고된 SHA-256 `0661ddaceb97610b046544276a18a1b02bda8aa3c53a16429315845e2a0ea180`을 대조한다. ZIP이 없으면 새 source-subset reconstruction으로 진행하며, 없는 ZIP의 hash/manifest를 검증했다고 쓰지 않는다.

기존 local Wolfram kernel을 직접 사용한다. MCP/cloud 대신 `wolframscript -local <actual kernel> -file <actual driver>`로 실행한다. 프로세스별 inner 120초, outer 150초, TERM 후 kill 10초 및 실제 존재하는 총자원 상한을 유지한다. xAct 설치나 activation이 필요한 작업이 아니다.

최초 실패와 원본 driver는 보존한다. 경로·로더·parser/API·평가순서·결과 수집·종료코드·패키징 결함은 같은 objective/scope/invariants 안에서 근거 기반으로 수정하고, 관련 회귀검사와 원래 target을 재검증한다. 한 번 편집했다는 이유만으로 돌아오지 않는다. 동일한 실패를 수정/새 근거 없이 반복하지 않는다.

네 historical scientific source, 원래 17개 물리 TestID·입력·기대값·메시지 의미는 바꾸지 않는다. `AUX13_MOMENTUM_CONSUMER_SIGN`의 예상 residual `2*C1`는 관측 전에는 예측이며, 관측되면 raw Failure 그대로 보존한다. 기대한 control 실패를 지우는 것은 수리 목표가 아니다. 추가 harness 회귀검사는 원래 17개와 별도 집계한다.

별도 수리 candidate, 기존 capture-six/native17, AUX15, 새로운 물리/solver 진화, provider/과학적 주장 승격에는 진입하지 않는다. 이전 작업의 소모된 실행 예산은 갱신하지 않는다.

## 3. 양방향 Git-first 공유

주 대화가 만드는 handoff·prompt·관련 작은 코드/patch는 가능한 한 대상 저장소의 격리된 handoff branch에 실제 파일로 게시하고 commit 고정 링크를 전달한다. Local Codex도 성공·실패·중단과 관계없이 가능한 반환 자료를 실제 파일로 commit/non-force push한다. 게시가 작동하는 경우 로컬 Downloads 경로나 ZIP만을 최종 전달물로 남기지 않는다.

현재 AUX task에서 새로 승인되는 원격 변경은 다음에 한정한다.

- 새 격리 handoff/evidence branch 생성 또는 이 task 전용 branch의 non-force 후속 commit/push.
- task 관련 handoff, 실제 결과 JSON, 원본/수정 driver의 증거 사본, 작은 회귀검사, patch, manifest, 필요한 로그와 표의 게시.
- PR #131에 실제 commit/파일 링크를 알리는 append-only 댓글. 필요할 때만 별도 Draft PR을 만든다.

`main`, canonical/다른 작업 branch, PR #131의 historical source branch는 직접 수정하지 않는다. 기존 dirty worktree와 최초 실패를 보존한다. merge/force-push/rebase·삭제, repository 공개 범위·권한 변경, workflow 수정·수동 CI dispatch는 승인하지 않는다. 게시 때문에 자동 발생한 workflow가 있다면 실행 검증과 구분해서 보고한다. 게시 승인은 production source 수리 승인이 아니다.

기존 이 task 전용 evidence branch가 있으면 우선 재사용한다. 없다면 위 고정 control을 parent로 새 `evidence/bg02-aux13-aux14-return-<run-id>` branch를 만들고 관련 반환 파일만 더한다. 이 parent는 재현용 publication 기준이며 최신 production base라는 주장이 아니다. non-fast-forward가 발생하면 원격을 다시 읽고 타인의 작업을 덮어쓰지 않는다.

## 4. 압축파일 없이도 검토할 수 있는 반환 자료

저장소에 기존 적절한 경로가 있으면 그것을 사용한다. 없다면 `artifacts/handback/bg02_aux13_aux14/<run-id>/`를 사용한다. 최소 자료는 다음과 같다.

- `CHATGPT_HANDOFF_KO.md`: 실제 수행·원인·수정·검증·남은 blocker·다음 최소 조치. 추론과 관측을 구분한다.
- `RETURN_STATUS.json`: 실행한 source/driver identity, 환경, 명령, 실제 process exit, exact TestID별 결과 또는 미평가/unknown, original/repair/회귀/target의 구분.
- `logs/`: 최초 실패와 최종 target의 stdout/stderr 및 진단에 필요한 원본 기록. 값이 없으면 없다고 기록한다.
- 실제 original/repaired driver와 작은 회귀시험, 변경 patch 또는 완전한 수정 파일, 간단한 파일 manifest.

필수 handoff와 결과 JSON, 주요 검증 로그/patch를 ZIP 내부에만 넣지 않는다. `EVIDENCE.zip`은 보조 백업이며, 그것을 다운로드·재업로드해야만 리뷰 가능한 구조로 만들지 않는다. 이미 Git에 존재하는 큰 source/vendor/archive를 반복 중첩 복제하지 않는다.

큰 원자료는 기존에 승인되고 접근 가능한 저장소/보관 경로에 두고 Git에는 식별자·파일 크기·실제 hash·필요한 읽기 가능한 결과를 남긴다. LFS pointer, 만료될 URL, 로컬 절대 경로만 남기고 원본이 공유됐다고 주장하지 않는다. 새 공개 링크나 권한 변경은 하지 않는다. 원자료를 직접 취득하지 못하면 검증 범위를 낮춰 기록하며 링크 접근이 검증 성공을 대신하지 않는다.

인증 토큰·비밀키·개인정보·라이선스 파일을 push하지 않는다. 필요한 redaction은 공유 사본에만 적용하고 원본 존재/보존 위치와 변환 사실을 기록한다. 단순한 개인정보 점검을 별도 보안감사 프로젝트로 확대하지 않는다.

## 5. 게시 확인과 identity

로컬 commit 성공, 원격 push 성공, 원격 readback 성공, 물리 검증 성공을 구분한다. push 후 remote ref와 주요 handoff/JSON 파일을 원격에서 다시 읽어 실제 commit과 내용이 게시됐는지 확인한다. `git ls-remote`만으로 파일 본문 readback까지 했다고 쓰지 않는다.

실행 source commit/tree와 게시 commit/tree는 별도다. source subset일 때는 실제 네 blob과 driver identity를 반환한다. 새 repair driver의 hash가 원본과 달라도 합법적인 변경 이력으로 기록하며 그것 자체를 물리 오류로 취급하지 않는다.

최종 출력에 publication commit/tree와 commit 고정 파일 링크를 넣는다. 자신의 publication commit SHA를 같은 commit 안의 JSON에 넣으려는 순환 수정은 하지 않는다. 실행 receipt는 실행 identity를 담고, 게시 후 최종 출력 또는 기존 PR 댓글이 publication identity를 담으면 충분하다.

테스트가 실패해도 상태를 정직하게 표시한 evidence 게시를 계속한다. push 실패는 `PUBLICATION_BLOCKED`, 계산 실패는 해당 runtime/harness/physics 상태로 분리한다. 게시만 실패했다고 과학 실행을 다시 돌리지 않는다. 이미 동작하는 인증 경로·branch binding 등 안전한 범위의 게시 문제는 근거 기반으로 수정할 수 있지만, 권한·보호규칙·비밀정보 정책을 우회하지 않는다.

## 6. Codex 최종 출력 — 사용자는 이것만 주 대화에 전달

```text
STATUS=<실제 실행/수리 결과>
REPOSITORY=cosmosapjw-quantum/bass
BRANCH=<실제 evidence branch>
EXECUTION_SOURCE=<실제 commit/tree 또는 source-subset 식별>
PUBLICATION_COMMIT=<실제 원격 게시 commit>
PUBLICATION_TREE=<실제 원격 게시 tree>
HANDOFF_URL=<commit 고정 CHATGPT_HANDOFF_KO.md 링크>
RESULT_URL=<동일 게시 snapshot의 RETURN_STATUS.json 링크>
PR_OR_COMMENT_URL=<게시했다면 실제 링크, 아니면 없음>
REMOTE_READBACK=<실제로 확인한 범위와 결과>
NEXT=<주 대화의 다음 최소 조치>
```

주 대화는 링크 또는 위 출력에서 repo/commit/path를 확인하고 GitHub connector로 handoff·JSON·관련 diff/로그를 직접 읽는다. 읽기 가능한 원격 자료가 있으면 사용자의 수동 다운로드·재업로드를 기본 단계로 요구하지 않는다. 최종 과학적 수용은 관련 원자료와 source를 검토한 뒤에만 한다.

실제 게시 경로가 차단됐을 때만 로컬 보존·복사 가능한 최소 handoff 출력·정확한 blocker를 반환한다. 이는 예외이지 정상 전달 방식이 아니다. 링크를 만들어내거나 미게시 파일을 공유됐다고 쓰지 않는다.

## 7. 이 파일을 받는 Codex에 대한 실행 지시

이 파일과 위 R2 및 원본 driver 댓글을 읽고, 기존 결과부터 재사용하여 AUX13/AUX14의 필요한 로컬 실행·범위 내 수리·검증을 수행하라. 완료/실패 결과와 변경된 driver를 이 문서의 Git-first 범위로 commit/non-force push하고 원격 readback 후 위 최종 출력으로 반환하라. 사용자가 ZIP을 직접 옮겨야 하는 절차로 되돌리지 마라.
