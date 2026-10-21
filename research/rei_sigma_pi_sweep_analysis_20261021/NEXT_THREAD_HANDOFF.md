# 다음 대화에 복사할 ACCEL03 재개문

아래 블록을 새 대화에 전달해. 실행용 고정 pin과 복사 가능한 명령은 같은 경로의
`CODEX_HANDOFF.md`에 있어. 이미 완료된 분석을 사용하는 것이 기본 행동이야.

```text
$physmath-research-loop를 사용해 BASS/rei_bianchi ACCEL03 이후 작업을 이어줘.
먼저 새 NCP 반환이나 다른 접근 가능한 Git/backup의 실제 delta를 확인하고,
이미 끝난 조사·실행·수치 수용·fresh 독립 심사와 그림을 재사용해.
현재 단위는 완료됐고 새 과학 범위는 아직 사용자가 정해야 한다.
새 반환 자료가 있다면 재실행 전에 먼저 수용·재사용·동일 cohort 여부를 판단해.

기준:
- branch: research/rei-sigma-pi-sweep-analysis-20261021
- BASS PR179: https://github.com/cosmosapjw-quantum/bass/pull/179
- REI PR217: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/217
- path: research/rei_sigma_pi_sweep_analysis_20261021
- 검토된 Stage B 실행 소스 pin과 source export 명령은 CODEX_HANDOFF.md에 있다.
- 후속 Stage C 문서·delivery commit과 실행 source identity를 구별해.

먼저 REPORT_KO.md, DAG.json, LOOP_RECORD.json, 현재 scoped decision,
evidence/INDEPENDENT_REVIEW.json, delivery/의 최종 publication/backup receipt와
CODEX_HANDOFF.md를 읽어. 그다음 새 의무에 필요한 소스만 읽어.
Conversation 검색 호출이 unavailable을 반환했다는 접근 한계를 명시하고,
미접근 대화·비공개 자료까지 전수 조사했다고 표현하지 마.

이미 끝난 실제 결과:
- 원 warm C15 pilot: 729 cases, 243 groups PASS, 누락 0, history 47,385행.
  원 history는 원 archive/index/hash/locator에 있고 이번 projection은 endpoint만이다.
- 실제 NCP native 5사례×2-step은 완료됐고 변경 없는 ACCEL02 기준으로 수치 수용됐다.
  NCP의 최초 python 명령 exit127은 /usr/bin/python3로 복구됐다.
- ACCEL03 plan 기반 집계: NCP 5 expected/5 success/0 missing/15 history rows;
  baseline 729 reused/0 pending/0 available history rows.
- 동일 scientific case body는 group reuse metadata가 달라도 중복 제거한다.
  누락은 PARTIAL과 ID, 예상 밖/충돌/binding/nsteps/gate 실패는 명시적 진단이다.
  Completed alias는 science ID→pinned csv_case_id로 찾고 요청 label을 유지한다.
- 상쇄 q=abs(p+r)/(abs(p)+abs(r)), 조건수와 null/status, 동일 cohort control 비교 구현.
  작은 signed total을 clip하지 않고 성분 규모의 128 eps 산술 검사를 사용한다.
- Massive fixed-weight J2_x=-5J2+J4, J2_b=-G를 유도·CAS·작은 저장 검증으로 확인했다.
  이는 radiation collision/emission/UV를 대체하는 새 closure가 아니다.
- 실제 점만 쓰는 NCP 그림과 archived endpoint slice 그림이 이미 렌더됐고 검토됐다.
  Source point table과 plot provenance가 각 results/*/plots/에 있다.
- 새 ODE/compile/benchmark 없이 구현·저장 결과 검증과 fresh 독립 심사를 끝냈다.
  새 scope가 없으면 원 729, 상세 benchmark, 전체 옛 suite, kernel matrix를 다시 돌리지 마.

바로 사용할 결과:
results/ncp5/ 및 results/ncp5/plots/actual_samples_4ff69a0d5fef.png
results/baseline729/ 및 results/baseline729/plots/endpoint_slice_caed0ccd4a58.png
선택적 재생성은 results/inputs/ncp5의 저장 fixture를 aggregate.py→plot_sweep.py로
읽으면 된다. Analyst의 Python/NumPy version을 옛 결과의 검증 기준으로 삼거나
PreparedContext/ODE/native library를 만들 필요가 없다.

실행 환경:
- Sandbox quota 8 CPU/8 GiB.
- NCP 저장 snapshot: 2026-10-21 21:56:39–42 KST, affinity 64 CPU,
  total 125.78 GiB, available 약 80.20 GiB. 현재 live 여유량은 직접 관측하지 못했다.
- Python은 사용 가능한 python3를 쓴다. numeric threads는 1이다.
- 새 사례가 명시적으로 제공되면 기존 native plan→pending-only build/prepare→
  shared_executor→aggregate→plot 경로를 쓴다. 지금 새 case/grid는 제공되지 않았다.
- --profile ncp --max-workers 64는 ceiling이다. 실제 affinity/quota/idle/RAM과
  pending 수가 dispatch를 제한한다. 작은 확인의 worker 상한은 2다.
- 다른 job이 바쁘다는 이유로 그 프로세스를 종료하거나 작업을 멈추지 말고,
  실제 가용 자원에 맞춰 진행한다. Thread pool 중첩은 만들지 않는다.
- 기존 repo의 fetched/pinned Git 객체에서 네 lane만 고유 폴더로 git archive한다.
  공유 branch checkout, clone/worktree, 다른 tracked 파일 변경은 필요 없다.

후속 범위:
사용자가 다음 과학 질문 또는 실제 새 pending 입력을 정해야 한다.
원 729 고정 aggregator에 custom 2-step 결과를 넣어 64-step 그림으로 표시하지 마.
Total stress는 signed component 합 뒤 norm을 취하고 control은 같은 source/backend/
toolchain/context/nsteps/구간의 정확한 zero-stress control만 사용해.
Full EoR, 일반 non-LRS/full Q^a,시간/radial/angular 수렴과 measured speedup은
이번 검증의 결론이 아니다. 새 범위의 계약을 먼저 고정하고 필요한 일만 이어가.

각 실제 단계에서 raw 증거, DAG node, publication commit, provider backup ACK와
다음 실행 전이를 함께 기록해. ACK 없이 backup 완료를 선언하지 마.
실행 당시 PENDING_INDEPENDENT_REVIEW 기록과 이후 수용 결정을 구별하고,
이미 끝난 과학 단위를 반복하는 대신 반환된 새 결과나 사용자가 정한 새 범위에 집중해.
```
