# S12: Rust 출생 기억 접선과 제한된 계산 최적화

2026-10-21 KST / 2026-10-20 UTC. 현재 단계는 C2–C5 소스 고정이다.

S11 이후 새 실행 결과를 찾기 위해 현재 PR174/175, research refs96개,
최근 PR10개, main, 연결된 대화 검색, Dropbox·Drive의 BASS_BACKUPS와
관측된 하위 폴더를 읽었다. 이 대조 범위에서 S11 이후 새 BASS 실행은
발견하지 못했다. 검색 범위 밖의 모든 대화·저장소가 비어 있다는 뜻은 아니다.

S11의 중단된 최종 게시를 복구했다:
[최종 댓글](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6301060073).
S11 소스7fb9b83c, 결과85d5833b, 배송 metadata44bac536은 서로 다른 identity다.
S11 ZIP4개와 최종 JSON의 Dropbox 전체 readback은 완료됐다. 새 Drive
업로드는 provider 응답과 ID를 받지 못했으므로 이중 배송 완료가 아니다.
원 S10의 양쪽 provider 검증 완료는 그대로 재사용한다.

## 이번 구현 대상

S9/S10의 JVP는 고정된 bank에 대한 state 미분이다. 그 계약은 올바르며
그대로 둔다. 새로운 Rust client에 각 출생에서 저장되는
`B_j`, `mu_theta`, `alpha_theta`를 추가해, S8 Python에서 이미 유도·실행한
전체 출생 기억 parameter tangent를 구현한다. 현재 상태의 기하 미분과
과거 출생 기억 forcing을 분리해 이중 계산을 막는다.

새 evaluator는 angular kernel을 준비하고 한 번의 순회에서 필요한
moment와 미분을 모은다. 기준 구현과 같은 정확도·같은 출력에서만
속도를 비교한다. 전체6상태 stiff Jacobian의 아래쪽 왼쪽 block 및
자율 clock 열을 포함한다. 블록 대각 근사는 정확 Jacobian으로 전달하지 않는다.

미완료 native 사례는 S8 `b9_n64_P2P4` 한 건이다. 원 failed raw에는
완전한 bank checkpoint가 없으므로, 새 namespace에서 한 case를 처음부터
실행하도록 준비한다. 완료17행은 재실행하지 않는다. 새 projector는
실패 지점부터 생성되는 명시적 등방 birth에만 적용하며 과거 weights를
소급 변경하지 않는다. n64 angular 오차는 원 target 대비 진단으로 남긴다.

## DAG와 실행 상태

| 단계 | 현재 상태 | 다음 증거 |
|---|---|---|
| C1 최신 대조·계약 | e48e0d56 게시·Dropbox 전체 readback 완료 | CONTRACT.json, intake, delivery/stage1 |
| C2–C3 방정식·수치 map | 유도·CAS51항등식·원문 대조 완료 | THEORY_KO.md, WOLFRAM_DERIVATIVES.json |
| C4–C5 자원·구현 | 구현·고정 검증설계·정적 finding 수정 완료 | PREREGISTRATION.json, src/, ncp/, static_review/ |
| C6–C8 검증·관측량·성능 | NOT_RUN | 새 source commit 이후 실제 receipt |
| C9 독립 검토 | 정적 검토만 완료, 실행 증거 검토 대기 | 구현자와 분리한 수식·코드/증거 검토 |
| C10 배송·handoff | 진행 예정 | Git 게시, 양쪽 provider별 실제 상태 |

최신 사용자 요청의 NCP64코어/128GiB는 새 자원 목표다. 현재 원격 도구의
첫 config 읽기는 월 사용량 제한을 반환했고 재시도·재연결을 하지 말라고
명시했다. 실제 장치 자원과 실행을 확인하지 못했으며 원격 process 실행은0회다.
NCP용 배치는 실제 CPU affinity·quota·남은 RAM·기존 작업을 확인하고,
동일 source/input/output 증거를 갖춘 완료 작업만 건너뛰도록 준비한다.

이번 source checkpoint 이전 새 compile/history/benchmark는0회다. 원문과
Wolfram 계산, AST/rustfmt, pinned dependency readback은 별도로 기록했다.
고정 소스 게시 후에만 C6의 새 짧은14 Rust history, 독립 Python history1,
최종 checkpoint restore1, 24점 core 및 동일 정확도 paired timing을 실행한다.
Sandbox case 병렬 검증은4개 pack·2worker이고 NCP용64개 pack과 구분한다.
각 pack 안의 ray/cohort 순회 순서는 바꾸지 않는다.

`prepare.py`는 source binding과178개 pinned VigilODE source를 확인하고
사설 work directory에서 compile만 한다. 기존 owner를 복사해 쓰는 경우에도
고정 파일만 읽고 검증하며 원본을 변경하지 않는다. `process_control.py`는
각 wrapper가 만든 child group의 중단과 잔여 child를 처리한다. 인프라 검증14개는
실제 helper·원자적 receipt·resume·resource gate를 검사하는 새 테스트다.
소스 동결 시점에는 아직 실행하지 않았다.

정확한 물리·소유권·admission·scope·자원 제한은 [CONTRACT.json](CONTRACT.json)에 있다.
실제 MD14/shared-Q와 evolving reactive full spectral history는 물리 입력과
별도 구현 의존성이 남아 있으며 대형 하드웨어로 완료 처리하지 않는다.
