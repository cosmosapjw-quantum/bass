# ACCEL01 다음 대화 스레드 handoff

다음 블록을 새 대화에 복사하면 된다. 최종 게시·백업 완료 여부와 commit은 `delivery/FINAL_PUBLICATION.json` 및 그 파일이 가리키는 실제 receipt를 읽어 확인한다. 중앙 receipt가 없거나 pending인 단계는 그대로 보고한다. 이 문서는 새 ACCEL01 백업 완료를 미리 선언하지 않는다.

## 복사할 메시지

```text
$physmath-research-loop의 ACCEL01 완료 결과를 이어서 사용해줘.

현재 branch는 research/rei-sigma-pi-acceleration-20261021,
경로는 research/rei_sigma_pi_acceleration_20261021이야.
BASS PR177: https://github.com/cosmosapjw-quantum/bass/pull/177
REI PR214: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/214
이전 계산 기준은 BASS PR176와 REI PR213,
research/rei_sigma_pi_pilot_20261021이야.

가장 먼저 현재 lane의 delivery/FINAL_PUBLICATION.json과 실제 delivery receipt들을 읽어 최종 source/publication/backup commit, 파일 hash, gate 상태를 확인해줘. 그다음 DAG.json, REPORT_KO.md, CODEX_HANDOFF.md, evidence/VERIFICATION.json, evidence/INDEPENDENT_REVIEW.json, evidence/RUNTIME_CURRENT.json을 읽어줘. 이전 pilot의 REPORT_KO.md, physics/SPLIT_RESULT_REVIEW.json, delivery/도 이어서 참조해줘. 중앙 receipt에 없는 게시·백업 완료를 가정하지 마.

독립 matter/radiation pi_ab를 설정한 non-tilted LRS Bianchi I split729 pilot은 이미 완료됐어. 729 cases, 243 PASS groups, missing 0, history 47,385행이며 component/cancellation 그림과 parameter-sweep slice 그림을 재사용하면 돼. 이전 pilot의 Stage5/Stage6 상태와 이번 ACCEL01의 새 백업 상태는 각 lane의 receipt로 구분해서 확인해줘.

과학 범위는 a=.1999→.2의 warm conditional LRS야. 기본 norm은 sqrt(A_ab A^ab/2)이고 signed 좌표도 유지해. Matter는 massive Vlasov, radiation은 gamma+massless nu+UV야. Total stress는 signed D_m+D_r를 합한 뒤 norm을 취해. 초기 응력이 상쇄돼도 서로 다른 성분 진화로 이후 total stress와 작은 shear가 생긴다는 기존 관찰을 유지해줘. full EoR, 일반 non-LRS, full Q^a closure, 수렴 입증은 남은 범위야.

이번 코드는 cached_context.py의 exact-bit per-model massive moment cache,
work_plan.py의 완료 case identity와 pending-only planner,
batch_worker.py의 원 shared_executor 연결과 case 단위 atomic checkpoint야.
원 owner·quadrature·reduction·물리 조건은 유지했고, 기본729 plan은 completed729/pending0/job0/no_work가 돼. 완료한729를 다시 계산하지 마.

검증은 구분해서 읽어줘:
- 최종25 targeted tests PASS: kernel144 points, 5개2-step cached/original 비교, identity/reuse/resource logic, toy I/O와2-process lock 등.
- C9 한 차례 독립 review: 29 guard probes PASS, open findings 0.
- 새 custom case 하나의 실제2-step CLI 검산: prepare/run-group exit 0, history2, 8 gates PASS.
- 마지막 출력 validator 수정은 그 저장 결과를 재검증했고 추가 solve 0이야. 실행 당시 source와 validator 수정 후 source가 다름은 worker_smoke/receipt에 기록돼 있어.
이것들은 성능 benchmark나 수렴 증명이 아니야. 상세 benchmark 0, 이전729 full rerun 0을 유지해줘.

NCP 64 CPU/128 GiB는 target이며 현재 NCP 실제 자원은 UNOBSERVED야. Desktop Commander monthly usage paused 오류와 로컬 NCP key 없음이 기록돼 있어. sandbox는 cgroup8 CPU/8 GiB이고2026-10-21 08:04 UTC 관측 headroom은7 CPU, 약6.72 GiB였어(1 GiB reserve 후 약5.72 GiB). 새 실행 때 실제 headroom을 다시 관측해줘. 다른 Codex 세션이나 작업이 있어도 전체 작업을 중지하지 말고 원 executor로 여유 자원 안에서 공존해줘.

다음 새 연구 범위는 내가 지정할게. 먼저 완료 근거를 재사용하고 임의로 full EoR·수렴·affine 근사·새 solver로 확장하지 마. 새 범위가 확정되면 CODEX_HANDOFF.md의 현재 CLI 절차대로 사용자 지정 JSON/CSV→work_plan scientific identity→batch_worker prepare→원 shared_executor.py --profile ncp --max-workers 64 --reserve-mb 1024 --resource-wait-s 300 --poll-s 0.5로 연결해줘. 모든 숫자 상한은 예약량이 아니며 실제 admission에서 재관측해야 해.

기존 aggregate는 원729 grid를 고정 검증하므로 새 custom/scientific input의 결과를 원729 aggregate/history/plots에 섞지 마. 새 aggregate가 필요하면 그 새 연구 범위의 expected-case contract와 provenance를 먼저 정해줘.

각 새 단계의 백업·게시·DAG 진척 상태를 함께 남기고, 최종 상태와 commit은 중앙 delivery receipt에서 확인하도록 유지해줘. 다음 Codex용과 다음 대화용 handoff도 복사할 수 있는 형태로 갱신해줘.
```

## 실제 재개에서 확인할 출력

| 확인할 내용 | 기준 파일 또는 동작 |
|---|---|
| 최종 게시·백업·source commit | `delivery/FINAL_PUBLICATION.json` 및 참조 receipt; 누락 또는 pending은 그대로 보고 |
| 기본729 재사용 | `evidence/REUSED729_WORK_PLAN.json`, `evidence/reused729_no_work/no_work.json`; completed729/pending0 |
| 현재 코드 검증 | `evidence/VERIFICATION.json`: 25 PASS 및 검증 source SHA256 |
| 독립 검토 | `evidence/INDEPENDENT_REVIEW.json`: C9 PASS, 29 guard probes, open findings0 |
| 단일 실제 worker 검산 | `evidence/worker_smoke/EXECUTION_RECEIPT.json` 및 `VALIDATOR_RECHECK.json`; 이전 source snapshot과 재검증 구분 |
| 자원 | `evidence/RUNTIME_CURRENT.json`은 과거 snapshot; 실제 launch 시 원 executor가 재관측 |
| 새 입력·실행명령 | `CODEX_HANDOFF.md` 6–8절; custom case schema, scientific ID, prepare, 원 executor의 실제 CLI |

최종 implementation은25 tests와 C9 PASS 뒤 freeze돼 있다. 새 대화를 시작했다는 이유로 기존 계산이나 검증을 다시 수행할 필요는 없다. 사용자 지정 변경과 그 의존성에 필요한 작업을 이어간다.
