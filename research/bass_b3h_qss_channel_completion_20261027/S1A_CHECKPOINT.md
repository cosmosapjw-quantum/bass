# S1A: Phase A 실행·검토 checkpoint

Phase A는 단 한 번 실행하여 67/67 고정 수치 검사를 통과했다. 독립 검토자의 `reviews/INDEPENDENT_REVIEW.md`는 Phase A `PASS_SCOPED`이며 코드 repair·재실행을 요구하지 않는다. 과학적 채택은 root admission 파일에서 정한다.

R1–R6/C1–C6의 실제 Phase A 근거가 준비되었으며 R7–R10/C7–C10의 선택 finite dynamic completion은 아직 수행하지 않았다. Phase A에 대한 독립 C9 검토 근거는 뒤 단계에서 재사용하지만 이것을 전체 dynamic transaction의 C9 완료로 표시하지 않는다. 원 중앙 DAG는 27/88·증분0이다.

S0 실제 commit은 b581ad6f9ab92ee2efac816e2f2d2a63994c77c6이다. 초기 S0 문서와 EXECUTION_FREEZE/BUDGET_LEDGER의 준비중·실행0 문구는 당시의 역사기록이다. 현재 실행 상태는 별도 `inputs/EXECUTION_FREEZE_PHASE_A.json`, `BUDGET_LEDGER_PHASE_A.json`, `results/EXECUTION_LEDGER.jsonl`과 `delivery/PHASE_A_EXECUTION_RECEIPT.json`에 있다. Frozen 실행 source와 그 hash는 결과 검토 후에도 변경하지 않는다.

실제 명령은 `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python code/metered.py phase_a`였다. Child CPU1.129564초, wall1.2450745230016764초, RSS32892KiB, wrapper CPU0.029937999999999992초다. 새 combined allocation의 남은 값은 CPU58.870436초·wall178.75492547699832초이며, 과거 closed allocation과 unknown remainder null을 보존한다. 새 실행은 별도 root Phase B contract와 신호가 필요하다. Phase A 자동 replay는 없다.

`theory/`의 네 문서는 corrected snapshot이다. finite propagator의 restart carry term 교정은 source theory의 실제 보완 기록이며 Phase A 수치 결과를 바꾸지 않는다. 향후 finite 모델은 별도 root 계약이 선택한다. S1A는 그 미래 실행을 했다고 주장하지 않는다.

원 35MB history를 재다운로드하거나 native exporter를 실행할 필요 없이 직접 입력·원본 tables/source·저장 결과로 이 checkpoint를 복원할 수 있다. 이 ZIP의 S0 SOURCE_MANIFEST는 이전 source snapshot의 역사적 manifest이며, 현재 변경된 stage/DAG/receipt에 대한 manifest로 재해석하지 않는다. S1A exact source는 S1A_SOURCE_MANIFEST가 정의하고 실제 publication SHA/backup ACK는 게시 후 receipt에 추가한다. 단계마다 별도 commit/archive를 만들었다고 주장하지 않는다.
