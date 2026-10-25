# 실제 R1–R10 / C1–C10 진행 기록

이 표는 workflow physmath-research-loop 1.0.0을 이번 유한 단위에 적용한
기록이다. 과거 완료 계산을 새로 수행한 것으로 세지 않는다.
전체 과학 admission은 ADMISSION.json을 따른다.

| 단계 | 수행·근거 | 범위 |
|---|---|---|
| R1 질문 고정 | 고정 HANDOFF, 최신 central AGENTS, 실제 HEAD·병렬 PR 확인 | provenance/NODE_PREFLIGHT.json |
| R2 재사용 경계 | G1B와 B3a–f 완료 결과·비용·실패 재사용 | 원 authority/inputs 보존 |
| R3 원자료 복구 | B3c ZIP, REC NPZ/admission, native LINE02 exact source 복구 | 새로운 IVP 없음 |
| R4 모형·단위 | cold R/X/radiation, tau, fixed L, native reference law 분리 | FROZEN_CONTRACT.md |
| R5 유도 | birth tensor, diagonal/determinant 및 Duhamel conditional bound, SI/core 변환 | theory/TRANSPORT_AND_GEOMETRY.md |
| R6 독립 이론 검토 | native Wien/Planck·Ahat/defect·scope 확인 후 PASS_SCOPED_R6 | reviews/R6_SOURCE_THEORY_REVIEW.md |
| R7 계산 결속 | 512 birth와 514 endpoint를 unchanged B3f/core에 결속 | results 원자료 |
| R8 해석·한계 | representation residual과 physical radius null 구분 | REPORT_KO.md |
| R9 독립 raw/그림 검토 | 별도 reviewer가 실제 JSON·3 PNG·변경 코드를 검토 | reviews/R9_INDEPENDENT_FINAL_REVIEW.md |
| R10 전달·다음 노드 | 소스 ZIP, 이중 백업, expected-SHA 게시, DAG·인계 | DELIVERY_RECEIPTS.json, HANDOFF_KO.md |
| C1 실행 환경 | Python 3.12.14 실제 probe; C++ 불필요 | 실행 ledger |
| C2 동결 계약 | 출생·geometry·native source·조건부 경계와 수치 기준 고정 | FROZEN_CONTRACT.md |
| C3 소유 경로 | 기존 checkout의 새 consumer lane; REC/기존 BASS owner 무수정 | git 선택 경로 |
| C4 구현 위임 | 요청된 lower-tier gpt-6.1-sol; 실제 backend는 미관측 | IMPLEMENTATION.md |
| C5 최소 대조군 | 정확 moment, Decimal reference, clock, underflow, units, readiness, near-isotropy | tests/test_binding.py |
| C6 실행 전 검토 | C9 4개 정적 결함을 보존하고 한 번의 targeted repair | C9_PREEXECUTION_REVIEW.md |
| C7 한정 실행 | one test → one consumer → one plot, 3 child 모두 exit0 | EXECUTION_LEDGER.json |
| C8 raw 보존 | 13 PASS, 512/514 rows,4 RHS,3 PNG, 실제 stderr/stdout | results/ |
| C9 독립 판정 | 이론/source reviewer와 변경부 reviewer, 최종 raw/figure reviewer 분리 | reviews/ 및 ADMISSION.json |
| C10 소스·복구 | mandatory input/dependency self-contained ZIP; 큰 NPZ는 ZIP 포함·Git locator 유지 | MANIFEST, archive/backup receipts |

새 strong no-go를 제안하지 않았으므로 NG1–NG7는 NOT_APPLICABLE이다.
물리 입력이 없다는 사유는 이 유한 후처리의 실행 금지가 아니며,
그 입력을 요구하는 물리 완료 주장만 INPUT_DEPENDENT로 남긴다.

