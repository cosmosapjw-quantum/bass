# R1–R10 / C1–C10 단계별 종료표

이번 단위의 범위는 실제 locked photon snapshot bridge다. 작업 20/20을 완료했다.
전체 BASS 물리 목표 완료율은 null이며, 미완 source/IVP/restart/domain 의무를 유지한다.

각 단계의 근거를 보존한 **가장 이른 cumulative checkpoint**를 적었다. 별도20개
업로드를 했다는 뜻은 아니다. S0·S1의 Git/Drive/Dropbox ACK는 확인했고,
S2의 실제 최종 ACK는 게시 후 PR187 본문과 대화의 outer receipt가 기록한다.

|단계|작업과 과학 판정|완성도|근거 보존·게시 checkpoint|
|---|---|---:|---|
|R1|연구 위치·계약: COMPLETE_SCOPED|100%|S0|
|R2|근거·재사용: COMPLETE_SCOPED|100%|S0|
|R3|주장·전제 정렬: COMPLETE_SCOPED|100%|S0|
|R4|가설·표현 탐색: COMPLETE_SCOPED|100%|S0|
|R5|구성적 유도: COMPLETE_SCOPED|100%|S0|
|R6|독립 검증: COMPLETE_SCOPED|100%|S0|
|R7|판별 검증: COMPLETE_SCOPED|100%|S1|
|R8|결과 판정: COMPLETE_SCOPED|100%|S1|
|R9|정식 결과·코딩 연결: COMPLETE_SCOPED|100%|S1|
|R10|종료·재개: COMPLETE_SCOPED|100%|S2|
|C1|목표·baseline: COMPLETE_SCOPED|100%|S0|
|C2|식–데이터–코드: COMPLETE_SCOPED|100%|S1|
|C3|수치 설계: COMPLETE_SCOPED|100%|S1|
|C4|실행 DAG·자원: COMPLETE_SCOPED|100%|S1|
|C5|구현: COMPLETE_SCOPED|100%|S1|
|C6|구현 검증: COMPLETE_SCOPED|100%|S1|
|C7|과학 검증: COMPLETE_SCOPED|100%|S1|
|C8|수치·재현성: COMPLETE_SCOPED|100%|S1|
|C9|독립 검토: COMPLETE_SCOPED|100%|S1|
|C10|판정·인계: COMPLETE_SCOPED|100%|S2|

## Checkpoint의 실제 상태

|Checkpoint|Git publication|백업|과학 판정과의 관계|
|---|---|---|---|
|S0 recovered preparation|42255a67234cd8b6c24ba8cb6b467cbdfe9ed238;75/75blob|Drive success·Dropbox completed|준비 문서/이론/입력 보존; 구현의 수용은 별도|
|S1 validated science|03101fd962ad2ce81195a2fcd3fae57834c80bd6;108/108blob|Drive success·Dropbox completed|PASS_SCOPED 결과와 실패·교정·복구 근거|
|S2 final handoff|이 파일을 포함해 게시 예정; 실제 SHA는 최종 PR receipt|snapshot 작성 시 PENDING; 실제 ACK는 최종 receipt|R10/C10 인계 작업 완료; 업로드 성공은 이후 실제 응답으로 판정|

## 실행 의존성

R1–R5 이론/입력 계약 → R6 독립 검토 → R7 판별식 검증 → R8/R9 수용·구현 계약.
C1–C4는 이 계약을 표현/수치/자원 DAG로 고정하고 C5–C8 구현·수치 검증으로 연결했다.
C9의 실제 반례 → targeted repair → 영향 검사 → 독립 scoped 승인 이후 게시했다.
R10/C10은 기존 실패, 자원, source 경계, 실제 identity와 다음 의존성을 인계한다.

예전 S0 원본은 LOST_BEFORE_UPLOAD이며 ACK가 없다. 현재 S0는 별도의 recovered
preparation이다. S1과 S2가 그 차이와 원본 raw 일부 소실을 숨기지 않는다.

