# S11 결과 게시·그림·배송 경로 최종 검토

## 판정

**결과 게시 범위 PASS_SCOPED: 최종 read-only 감사 23/23, exit 0, stderr 0 bytes.**
대상 result commit은 `85d5833b4486d14855b84a9d967f5819788d05e5`,
tree는 `fd3e994212059228501e26f7bf3d3b96462ba1d5`다. 이 판정은 결과·그림·source 및 Git 연결에 관한 것이다. 새 S11의 Drive 배송 성공을 뜻하지 않는다.

검토자 `/root/new_branch_intake`는 Rust projector/CLI 작성자이며, root Python runner, 결과 문서, figure script의 작성자는 아니다. 따라서 이 검토도 단독 독립 Rust 구현 승인으로 사용하지 않는다. 별도 이론 검토자의 Rust 검토와 역할을 구분한다.

## 결과 문서와 수치

`RESULTS_KO.md`와 `RESULT_LEDGER.json`을 전체 읽고 저장 자료와 대조했다. 근거 없는 물리 범위 확대나 이전 증거의 상태 후퇴는 발견하지 못했다.

- 14개 projection 쌍의 12개 positive 결과와 두 P246 infeasible 결과가 일치한다.
- S8은 보존한 입력에 대한 새 pointwise P24 복구로 제한된다. 원 `INNER_P2_PRECISION_LIMIT` history와 receipt는 실패로 유지된다.
- Dyadic uniform의 49점 최대 bias 악화 비율 `1.54913989382294`가 유지된다. 연속구간 supremum이나 모든 finite-d의 개선으로 표현하지 않는다.
- 101 main 검사, 25 exact 수학 단위, 235 물리 C9, 152 provenance C9를 서로 겹칠 수 있는 별도 집계로 유지한다.
- S9/S10의 기존 완료와 원 9ZIP·4,399,983 bytes·중복 payload383항목은 재사용한다. Closed small의 불확실성과 changing n16/cohort2 `0.9498173837599284` 회귀도 남아 있다.
- 실제 MD14/native shared-Q, evolving reactive full finite-bin history, 더 넓은 finite-d/angular 정확도, full birth-memory tangent 의무가 열려 있다. `5.369926725506957e-12`는 제한된 source-deposition 값으로 남는다.
- 결과 작성 시점의 새 배송 pending은 역사적 상태로 명시되어 후속 closeout에 맡겨져 있다. 원 S10 배송을 pending으로 되돌리지 않는다.

Markdown의 상대 evidence 링크 61개와 ledger의 artifact 링크 34개는 모두 result tree에 존재한다.

## 독립 Git 및 파일 검증

Fresh GitHub commit readback은 result가 main source
`7fb9b83cba01d37ce4cabbc4772527710601cd96`의 직접 후속임을 확인했다.
Fresh 최상위 tree와 저장된 전체 recursive tree를 Git object 형식으로 다시 해시했다.

| 확인 대상 | 결과 |
|---|---:|
| Recursive tree 항목 | 3,056 |
| 다시 해시한 tree objects | 359 |
| 게시 payload의 전체 bytes/SHA256/Git blob | 120/120 |
| 게시 payload bytes | 4,109,404 |
| Source→result의 새 파일 | 76 |
| 기존 파일 수정 | DAG metadata 1 |
| 삭제·예상 밖 경로 | 0 |
| 실행 source/input의 동일성 | 18/18 |

최초 감사 R1은 22/23이었다. 결과 게시 후 working DAG가 다음 closeout 단계로 진행되어, 현재 checkout의 DAG 한 파일이 result manifest와 달랐기 때문이다. 이 실패와 원 stdout/exit 1을 그대로 보존했다.

해결은 working DAG를 되돌리는 방식이 아니다. Result tree의 관측된 blob
`8e844b3fb43ec8a5cf1a358c3c9661e6089116fa`를 읽기 전용으로 새로 받아,
146,107 bytes와 SHA256
`1389085c2db2750e0ba213949f1daa1afa61139fd6d87ed1f9779965d40def4a`를
검증했다. R2는 이 immutable DAG를 명시적 입력으로 사용하여 23/23을 확인했다.
Working DAG 및 source 파일은 수정하지 않았다. R2 감사 wall은 0.113692초다.

## 그림 검토

처음 읽은 그림과 CSV의 수치 검토는 17/17이었다. CSV588행은 저장된 49점 grid와 정확히 같고, 12개 최대값·argmax·signed bias와 source hash가 일치한다.

두 작은 표현 문제를 지적했고 root가 figure-only로 수정했다.

1. `positive birth moments`를 `positive birth weights`로 바꾸어, target even moments는 0이라는 사실과 맞췄다.
2. Panel b의 annotation을 오른쪽 아래로 옮겨, d=-0.6의 orange P246 endpoint가 가려지지 않도록 했다.

최종 PNG를 실제로 다시 보아 두 수정과 scope footer를 확인했다. 최종 파일/hash readback 8/8이며 CSV와 main-data hashes는 그대로다. 최종 PNG SHA256은
`8eb1024c59f6dd2d271c9322b8c521116199c5ab5cee3ea73d18c82e8a63c7b8`다.
이 검토자는 plot을 재실행하지 않았다.

## Drive 대체 경로의 실제 상태

Root가 허용한 한 번의 대체 경로는 **copy 호출에서 중단, 서버 측 생성 결과 UNKNOWN**이다.

| 단계 | 실제 관측 |
|---|---|
| 원 S10 복구 ZIP metadata | 성공: ID `1oUoDJ8O0Bh6W1yFzSdc3XebGNeSengfZ`, 210,434 bytes, application/zip, /BASS_BACKUPS |
| 로컬 C1 ZIP | 40,857 bytes, SHA256 `73653cbbd5e8b01b10f4e95513514bb8d8db6f5415a80724fa79d0e58185e028`, CRC PASS |
| `copy_file` | 호출함. 원 파일의 관측 URL, 지정 /BASS_BACKUPS, 새 pending 이름을 사용 |
| 새 copy ID 또는 성공 응답 | 반환되지 않음 |
| 도구 종료 | `aborted by user after 344.6s` |
| `update_file` | **호출하지 않음** |
| 원 ZIP의 content update | **호출하지 않음** |
| 이후 read-only 이름 검색 | 18:23:53 UTC 기록: pending/final 이름 모두 결과 0개 |

Copy의 예정 이름은 `BASS_S11_C1_PENDING_CONTENT_20261020_e9f8eccc.zip`,
최종 예정 이름은 `BASS_S11_C1_20261020_e9f8eccc.zip`이었다.
새 copy ID가 확인되지 않아 BEFORE-update checkpoint나 bytes update로 진행하지 않았다.
빈 이름 조회는 늦은 서버 처리 가능성까지 배제하지 않으므로 생성 성공이나 확정적 부재로 바꾸어 기록하지 않는다. 중단 후 Drive mutation을 재개하지 않았다.

이는 새 S11의 대체 전달 경로 상태이며 이미 완료한 S10의 검증·배송 상태를 변경하지 않는다.

## 보존 파일

- `FINAL_RESULT_AUDIT_R2.json`, `FINAL_RESULT_AUDIT_R2_PROCESS.json`: 최종 23/23과 실제 raw receipt.
- `FINAL_RESULT_AUDIT_R1.json`, `FINAL_RESULT_AUDIT_R1_PROCESS.json`: 최초 checkout drift 실패를 그대로 보존.
- `audit_final_result.py`, `audit_final_result_r2.py`: 각 실제 감사 source.
- `result_commit_fresh.json`, `result_tree_fresh.json`, `STAGE3_DAG_READBACK_RECEIPT.json`: immutable Git 근거.
- `FIGURE_PRE_REVIEW.json`, `FIGURE_FINAL_REVIEW.json`: 원 지적과 수정 확인.
- `DRIVE_ALTERNATE_INTERRUPTED_COPY.json`, `DRIVE_ALTERNATE_NAME_LOOKUP.json`: 실제 Drive 반환 기록과 미확정 상태.
- `FILE_MANIFEST.json`: 이 검토 묶음의 identities.

이번 final review와 Git 검증에서 solver/compiler/history/ODE/benchmark/NCP 실행은 모두 0회다.
