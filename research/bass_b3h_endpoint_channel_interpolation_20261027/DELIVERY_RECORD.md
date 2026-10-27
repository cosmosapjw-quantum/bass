# Endpoint-channel 유한 transaction 전달 기록

이 문서는 현재 노드의 최종 source checkpoint에 들어가는 전달 설명이다. 과학 판정은 PASS_SCOPED_CONDITIONAL_ENDPOINT_TRANSACTION이며, 실제 새 계산은 종료됐다. 최종 source ZIP의 업로드 ACK는 생성된 뒤 `delivery/FINAL_ROOT_ACK.json`과 최종 handoff에 기록한다. 미래 업로드 성공이나 자기 자신의 commit hash를 미리 기록하지 않는다.

## 실제 확보된 checkpoint

| 묶음 | 포함 R/C 단계 | 실제 소스 commit | 현재 실제 게시·백업 누계 | 원 DAG |
|---|---|---|---:|---:|
| S0 | R1, C1 | 6d66e0082da7120a844ea3538f51103ce5a5ce86 | 2/20 | 28/88 |
| ST | R2–R6, C2–C4 | 9e2bfb3ffe05bf0461dc53db27aa73820768ac33 | 10/20 | 28/88 |
| S1 | R7–R9, C5–C9 | e35673b96c94dfad576c76c5b0b12f4873dd13e4 | 18/20 | 28/88 |
| D/F | R10, C10 | source archive와 실제 ACK의 후속 전달 commit으로 결속 | 현재 최종 ACK 대기 | 28/88 |

각 완료 단계가 어떤 실제 source checkpoint와 backup ACK를 공유하는지는 `STAGE_LEDGER.json`에 있다. 20개의 별도 ZIP이나 20회의 과학 실행을 주장하지 않는다.

S0 ZIP은 1,161,548 bytes, SHA256 `d10d848327c3d83ddd8a8a94c13930949dfcf7286fe3cee91d6da5c9aabce649`다. Drive ID는 `1dR2qiF-4ojczZCZPRAs7y-sj4APt61nB`, Dropbox ID는 `id:BSpOijBcT10AAAAAAEDILg`, rev는 `65ed40c6ec9790af03d47`다.

ST ZIP은 2,037,295 bytes, SHA256 `85dc5a5514f419f253fcecb14f235d26fef3bdc4c4b525fc4af19539c4fb7422`다. Drive ID는 `1RaTZLsHTvKDFQCpVjSMeeDL1FzVdc2t4`, Dropbox ID는 `id:BSpOijBcT10AAAAAAEDINQ`, rev는 `65ed425aef9210af03d47`다.

S1 ZIP은 9,437,619 bytes, 107 members, SHA256 `b5e93a5a7fe6f8def95deefd9b169deb5d8f9757f978c980da2b1e3742a02f93`다. Drive ID는 `1v-lOAMYwIPv1G2VhUjUGaiclbaaVNQBx`, Dropbox ID는 `id:BSpOijBcT10AAAAAAEDIWg`, rev는 `65ed4b3ae6c290af03d47`다. 두 provider에서 실제 업로드 완료를 받았고 별도 metadata 조회의 byte count도 일치했다. Provider 원격 bytes를 재다운로드하여 SHA를 확인했다는 주장은 하지 않는다.

## 중앙 반영

실제 중앙 반영 commit은 **ff724389fc4b7b33d3492aa8ca3b76e1f108a080**이다. `research/orchestration-sandbox-20261022`의 최신 실제 HEAD **7de02b3e05705ead4eeb313c8487a21d4e6876a6** 위에 expected-SHA, force=false로 게시하고 HEAD를 다시 읽었다. 중앙 tree는 `e3396e58deee9fec59e1badbdfe2a35f1e2c199f`다.

88개 ID·순서, 다른 87개 DAG node와 status row, 17개 integration edge, 모든 기존 contract field·gate·dependency·authority를 유지했다. B3h의 현재 wrapper observation, 상태와 pass action만 갱신하고 이전 frozen-left 관측을 이력으로 보존했다. 새 return은 `research/orchestration_expansion_20261025/returns/BASS_B3H_ENDPOINT_CHANNEL_INTERPOLATION_20261027.json`이다. 실제 비교 결과는 `delivery/CENTRAL_COMPARISON.json`, 실제 게시 ACK는 `delivery/CENTRAL_PUBLICATION_RECEIPT.json`에 있다. 이전12f6007a나5abe0d19, 또는42cc snapshot으로 중앙을 덮어쓰지 않았다.

## Git 원자료와 source ZIP의 대응

검토된 원자료 JSON은 17,398,524 bytes, SHA256 `acf56f5aefe556d1d86e4f93f3063c5d38078cb8c7f9a627b141c4ef9582f3bd`다. 실제 Git 게시 경로가 단일 MCP 요청을16 MiB로 제한하여 원본 blob 업로드를 거절했다. 과학 실행을 반복하지 않고 저장 표현만 무손실 gzip으로 바꿨다.

GitHub의 `results/ENDPOINT_RESULT.json.gz`와 `ENDPOINT_PARTIAL.json.gz`는 동일한 Git blob `7fd987ee872946661061d6222e09d2ee5fe1f232`를 가리킨다. Gzip은 3,572,920 bytes, SHA256 `77692881eff264dc9dfe6c16ce8d4c7f17a9853e33f994a6c06b08f0a8cfb152`이며, 압축 해제하여 원본 bytes가 정확히 복원되는 것을 확인했다. Source ZIP에는 원본 JSON을 그대로 넣었다. S1 ZIP 생성 이후 추가된 게시 표현 metadata는 `delivery/GITHUB_RAW_REPRESENTATION.json`에서 구별한다. Git projection과 source archive의 byte 구성을 같다고 주장하지 않는다.

최종 source ZIP은 현재 unit의 코드, 유도, 실제 입력, 원자료, 실패·성공 실행 ledger, 독립 검토, 중앙 snapshot, 단계 ledger와 handoff를 포함한다. 이전 ZIP을 재귀적으로 중첩하지 않는다. 최종 업로드 receipt는 source archive 생성 뒤 Git의 전달 commit에서 제공하여 자기 hash/ACK를 archive 내부에 순환 참조시키지 않는다.

## 종료 조건

R10/C10의 source 설명과 중앙 반영을 마쳤으며, 최종 archive의 실제 provider ACK와 그것을 기록한 전달 commit이 확인되면 게시·백업은20/20이다. 과학 실행은 이미 닫혔다. 이후에는 저장된 결과를 읽고 현재 노드의 전달을 확인한다. `AUTO_NEXT_NODE=false`이며 새 연구 노드는 시작하지 않는다.
