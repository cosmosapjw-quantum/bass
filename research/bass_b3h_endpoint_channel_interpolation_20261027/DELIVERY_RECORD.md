# Endpoint-channel 유한 transaction 전달 기록

이 문서는 현재 노드의 실제 최종 전달 기록이다. 과학 판정은 PASS_SCOPED_CONDITIONAL_ENDPOINT_TRANSACTION이며 실제 새 계산은 종료됐다. D source 게시·HEAD readback, 최종 source ZIP의 실제 Drive/Dropbox 업로드·별도 metadata ACK와 영구 파일 저장을 완료했다. 선택된 R/C 단계는 **work20/20·published20/20·backed20/20**이며 canonical receipt는 `delivery/FINAL_ROOT_ACK.json`이다. 원본 D source ZIP 이후의 F receipt commit 자체 SHA는 root의 외부 readback으로 전달하며 이 문서에 미리 쓰지 않는다.

## 실제 확보된 checkpoint

| 묶음 | 포함 R/C 단계 | 실제 소스 commit | 현재 실제 게시·백업 누계 | 원 DAG |
|---|---|---|---:|---:|
| S0 | R1, C1 | 6d66e0082da7120a844ea3538f51103ce5a5ce86 | 2/20 | 28/88 |
| ST | R2–R6, C2–C4 | 9e2bfb3ffe05bf0461dc53db27aa73820768ac33 | 10/20 | 28/88 |
| S1 | R7–R9, C5–C9 | e35673b96c94dfad576c76c5b0b12f4873dd13e4 | 18/20 | 28/88 |
| D/F | R10, C10 | d7018942047ab5d62f65f005a79f7340981a8058 — 실제 D source; 후속 F canonical receipt | 20/20 실제 ACK | 28/88 |

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

R10/C10까지 **work20/20·published20/20·backed20/20**으로 완료했다. 실제 D source commit은 **d7018942047ab5d62f65f005a79f7340981a8058**, tree는 **12a8b2a46817cba90cebf2333d43d50027493a16**이며 parent **e35673b96c94dfad576c76c5b0b12f4873dd13e4** 위에 force=false 게시와 readback을 마쳤다. D ZIP은 **9,791,759 bytes,124 members**, SHA256 **67d3324de3531ada096f07f32f2c801340558bce7aee906e1ebff67b0cbd8794**다.

Drive upload success와 별도 metadata 크기 **9,791,759 bytes**의 ID는 **165W3QF9YP4Dqiw0spd8J6w2msPg8YiFy**다. Dropbox upload poll completed와 별도 metadata 크기도 **9,791,759 bytes**이며 ID **id:BSpOijBcT10AAAAAAEDIZQ**,rev **65ed4de03e7080af03d47**,path `/BASS_BACKUPS/BASS_B3H_ENDPOINT_CHANNEL_D_20261027.zip`,server-modified **2026-10-27T16:23:31Z**다. 원격 bytes를 재다운로드한 hash 검증은 주장하지 않는다. [최종 D source ZIP](https://chatgpt.com/library?file_id=libfile_58dfc7ae298c8191946ef69af0d9cbfb&account_id=personal)의 영구 저장도 완료했다.

실제 최종 ACK는 `delivery/FINAL_ROOT_ACK.json`에 있다. 불변 D source ZIP과 그 이후의 F receipt commit은 서로 다른 전달 객체이며, F 자체 pin은 root가 외부 readback으로 전달한다. 과학 실행은 닫혔고 추가 실행 권한은 없다. 저장된 결과를 재사용하고 이 노드를 종료한다. `AUTO_NEXT_NODE=false`이며 새 연구 노드는 시작하지 않는다.

## 최종 F 직전의 최신 중앙 관측

Root의 실제 **2026-10-27T16:27:20Z** 재조회에서 최신 중앙 HEAD는 **b99a9468abd53de77ddae36d93180e60072885bc**였다. 이는 이 노드의 실제 반영 M **ff724389fc4b7b33d3492aa8ca3b76e1f108a080**을 직접 parent로 하는 정상적인 HE 후속 commit이며 compare는 **ahead1/behind0**, 변경은 **HE 전용9개 경로**다. 메시지는 `HE KINEMATIC08: record exact physical-input reference, preserve plot CPU failure and28/88`다. 실제 CURRENT_STATUS blob `237060bb7784b4c7f127fada79bd75f29f1e7c7a`의88개 row에서 우리 B3h 객체는 M과 정확히 같은 의미를 유지했고, `HE-CLOSURE`·`HE-EXP-NUCLEAR`·`HE-EXP-CLOSURE`의 observation만 바뀌었으며 세 status는 그대로다. 원 DAG **28/88**도 유지된다.

우리 `central_reflection_commit`은 역사적 실제 M으로 보존한다. 다음 대화는 최신 **b99a9468abd53de77ddae36d93180e60072885bc** 위의 중앙 상태를 기준으로 삼고, 보관된 ff724/M snapshot으로 이를 덮어쓰지 않는다. D ZIP와 source snapshot은 갱신하지 않았으며 추가 과학·노드 실행이나 중앙 push도 없다. 상세 실제 관측은 `delivery/FINAL_ROOT_ACK.json`의 `latest_central_observed`에 있다.
