# ACCEL01 Codex handoff — 완료된 split729 재사용과 새 사례 실행 연결

이 문서는 `physmath-research-loop`의 ACCEL01 구현을 이어받는 Codex용이다. **다음 연구 범위는 사용자가 정한다.** 먼저 완료 근거를 읽고, 지정된 새 범위에 필요한 변경만 수행한다.

## 1. 먼저 읽을 파일과 상태의 기준

현재 작업 경로는 `research/rei_sigma_pi_acceleration_20261021`, branch는 `research/rei-sigma-pi-acceleration-20261021`이다.

- BASS 구현 및 연구 기록: https://github.com/cosmosapjw-quantum/bass/pull/177
- REI 연결 및 소비 기록: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/214
- 이전 계산: BASS PR176, REI PR213, `research/rei_sigma_pi_pilot_20261021`.

읽는 순서는 다음과 같다.

1. **`delivery/FINAL_PUBLICATION.json`과 그 receipt가 가리키는 게시·백업 기록.** 최종 source commit, publication commit, backup locator, 크기와 hash, gate 상태는 이 중앙 기록에서 읽는다. 같은 `delivery/`에 다른 최종 receipt 이름이 있다면 실제 파일 목록과 그 참조 관계를 확인한다. 파일이 없거나 해당 단계가 미완료라면 그 상태를 그대로 보고한다.
2. `DAG.json`, `REPORT_KO.md`, `README_KO.md`, 이 문서 및 `NEXT_THREAD_HANDOFF.md`.
3. `evidence/VERIFICATION.json`, `evidence/INDEPENDENT_REVIEW.json`, `evidence/RUNTIME_CURRENT.json`.
4. `evidence/REUSED729_WORK_PLAN.json`, `evidence/reused729_no_work/no_work.json`, `evidence/worker_smoke/EXECUTION_RECEIPT.json`, `evidence/worker_smoke/VALIDATOR_RECHECK.json`.
5. 이전 lane의 `REPORT_KO.md`, `SPLIT_CONTRACT.json`, `physics/SPLIT_RESULT_REVIEW.json`, `CODEX_HANDOFF.md`, `delivery/`.

최종 commit을 이 문서 안에 다시 고정하지 않는다. 문서 자체를 포함한 commit/hash가 서로를 참조하는 순환을 피하기 위해 중앙 receipt가 그 관계를 관리한다. **이 문서만으로 새 ACCEL01 게시·백업이 완료됐다고 판단하지 않는다.** 이전 pilot의 Stage5/Stage6 완료는 이전 lane의 실제 receipt로 확인하는 별도 사실이다.

## 2. 완료된 과학 결과와 유지할 경계

독립적인 matter/radiation 초기 응력을 설정한 non-tilted LRS Bianchi I pilot은 **729 cases, 243 PASS groups, missing 0, history 47,385행**으로 완료돼 있다. component/cancellation 그림과 parameter-sweep slice 그림도 완료 데이터에서 재사용한다. 현재 optimization의 목표는 이 결과의 계산 경로와 재개 능력을 개선하는 것이다.

물리 owner는 `80825585f9fe31d2ee0d5af545ada3fa1f52be72`, 이전 실행 source는 `82372ed8db68085868603d4267a630ed9cde6abb`, BASS baseline은 `26f4a89a54462c4e7c5705f281f187f33f45166a`, REI baseline은 `d32cd99fa19c65aa1ca63dbc8aab8741834270e8`이다. 새 구현의 최종 source identity는 중앙 delivery receipt를 따른다.

범위는 **warm conditional, a=0.1999→0.2, L=8, 8X8 source grid, massive_fraction=0.1, mass_over_T=30**이다. 기본 norm은 `sqrt(A_ab A^ab/2)`이고, Frobenius norm은 그 값의 `sqrt(2)`배다. signed 좌표도 함께 보존한다.

- Matter: `D_m = Pi_massive`인 massive nonbaryonic Vlasov 성분.
- Radiation: `D_r = Pi_gamma + Pi_nu + Pi_UV`; 선택한 owner의 neutrino는 massless이다.
- Total: 먼저 `D_m + D_r`를 계산한 뒤 norm을 취한다. 상쇄하는 두 성분을 각각 절댓값으로 만든 뒤 합치지 않는다.
- 두 성분의 다른 진화 때문에 초기 total stress가 상쇄돼도 이후 total stress와 작은 shear가 생긴다는 기존 관찰을 유지한다.

전체 EoR, 일반 non-LRS, full emitter/donor/escape `Q^a` closure와 수렴 입증은 남아 있다. 다른 branch의 collisionless 장구간 결과를 이 driven warm lane의 계산 결과로 합치지 않는다. `alpha_m`에 대한 affine basis나 `(x,b)` 보간표, 새로운 reduction 순서·solver는 현재 구현에 포함되지 않는다. 사용자가 새 연구 범위로 지정하기 전에는 이를 확장하지 않는다.

## 3. 구현 구조와 identity

| 파일 | 역할 | 고정할 조건 |
|---|---|---|
| `cached_context.py` | 같은 모델의 동일한 binary64 `(x,b)`에 대해 원래 massive three-moment 결과를 bounded cache로 재사용 | 원 owner 함수·quadrature·reduction 순서 유지; 질량·params·배열 값과 dtype/shape/strides/layout binding 검증 |
| `work_plan.py` | pinned 완료729 registry, canonical signed coordinates, 새 사례 scientific identity, pending-only resource plan | 중복·누락·좌표 오류·파일 변경 거부; 기본729는 pending 0 |
| `batch_worker.py` | pending plan을 원 `shared_executor` manifest로 변환하고 그룹별 cached context로 실행 | source/input/toolchain 검증; 완료729의 64-step 재큐잉 거부; case 단위 atomic checkpoint |
| 이전 lane의 `shared_executor.py` | 실제 프로세스 admission, scope lock, memory/CPU 재관측, 실패 보존 | 기존 scheduler를 사용하며 타 세션을 중지하지 않음 |

Scientific identity는 canonical baseline source binding의 상대 경로, 고정 계약, 요청 좌표와 seed에서 정해지는 전체 per-case Parameters, nsteps/compress/feedback, actual 또는 archived toolchain을 결합한다. 전체 seed record도 원래 mapping으로 재검증한다. `science_context_id`와 case별 `science_id`를 plan에서 읽는다. case label, grouping, worker 수, host 경로는 같은 과학 계산을 새 계산으로 만들지 않는다.

Backend identity는 baseline과 실제 실행에 쓰는 새 Python 파일들의 source binding을 포함한다. 개별 결과 저장 경로는 `CASE_STORE/backend_source_id/science_id/`다. 각 entry의 `case.json`과 `receipt.json`은 per-case `fcntl` lock 및 atomic directory publication으로 생성된다. source/backend 변경은 해당 namespace를 바꾼다. 성공한 entry의 결과 bytes/SHA256·receipt·source·toolchain·owner config·gates·history를 확인한 뒤 재사용한다. 손상된 committed entry는 실패로 보고하며 조용히 재계산하거나 덮어쓰지 않는다.

그룹 일부 실패 시 성공한 case entry는 남는다. 새 그룹이나 새 output scope에서도 동일 case store를 사용하면 성공 사례를 재사용한다. labels가 바뀌면 반환 결과의 outer case label만 현재 요청에 맞추고 원래 receipt provenance는 보존한다.

## 4. 검증을 구분해서 읽기

| 근거 | 실제 범위 | 의미 |
|---|---|---|
| `evidence/VERIFICATION.json` | 최종 25 targeted tests PASS | 144 kernel points, 5개 2-step cached/original 비교, identity/reuse/resource logic, toy I/O 및 2-process lock 등 변경 의존성 검증 |
| `evidence/INDEPENDENT_REVIEW.json` | C9 한 차례 독립 review, 29 guard probes PASS, open findings 0 | cache metadata mutation, 반환 thread-env alias, owner 출력 검증의 수정 후 확인 |
| `evidence/worker_smoke/EXECUTION_RECEIPT.json` | 원729에 없는 custom case 하나의 실제 2-step CLI 연결 확인 | prepare/run-group exit 0, history 2행, 8 gates PASS |
| `evidence/worker_smoke/VALIDATOR_RECHECK.json` | 위 저장 결과에 새 validator를 적용하고 변조 복사본 거부 | 추가 solver 호출 0; 실행 당시 source와 validator 수정 후 source가 다름을 명시 |
| 원 split729 review와 완료 registry | 이전 완료 계산 | 729 full trajectories를 다시 실행하지 않고 재사용 |

상세 성능 benchmark는 **0**, 이전729 full-trajectory 재실행은 **0**이다. 이 검증을 속도 향상 배수, 전체 EoR 정확도 또는 수렴 증명으로 해석하지 않는다. 코드가 고정돼 있으면 receipt와 hash를 먼저 확인하고, 이전 검사를 관성적으로 반복하지 않는다.

## 5. 현재 가용 자원과 NCP 상태

`evidence/RUNTIME_CURRENT.json`의 마지막 headroom 관측은 **2026-10-21 08:04:11 UTC**다. 이 값은 당시 snapshot이며 다음 실행의 예약량이 아니다.

| 구분 | 확인된 상태 |
|---|---|
| NCP target | 64 CPU / 128 GiB |
| 이번 세션의 NCP 실제 가용 자원 | **UNOBSERVED** |
| NCP 연결 제한 | Desktop Commander monthly usage가 paused 상태라는 service error; 해당 응답은 retry/reconnect를 하지 말라고 안내했고 로컬 NCP key도 없음 |
| Sandbox cgroup 한도 | 8 CPU / 8 GiB; affinity에 보인 9 logical CPU를 usable quota로 읽지 않음 |
| 당시 추가 CPU budget | 7 workers, worker당 numerical thread 1 |
| 당시 cgroup memory headroom | 약 6.72 GiB; 1 GiB reserve 후 admission memory 약 5.72 GiB |
| 원729 pilot 실제 실행 환경 | 8 CPU / 8 GiB |

다른 Codex 세션이나 작업이 있다는 이유로 전체 작업을 중지하지 않는다. 새 작업은 실제 affinity/cgroup/idle CPU/memory 여유 안에서 admission한다. NCP 접근이 회복되면 그 host에서 새로 관측한다. `--profile ncp --max-workers 64`는 상한이며 64 CPU를 점유했다는 뜻이 아니다. existing executor의 재관측과 대기 기능을 사용하고, 현재 사용자에게 할당되지 않은 자원을 가정하지 않는다.

## 6. 기본729 입력은 no-work로 연결

다음 명령은 BASS checkout root에서 실행한다. output 경로는 새 작업마다 명확하게 분리한다. 이 블록은 완료된 입력을 확인하며 ODE를 실행하지 않는다.

```bash
ACCEL_LANE="research/rei_sigma_pi_acceleration_20261021"
PILOT_LANE="research/rei_sigma_pi_pilot_20261021"
ACCEL_RUN="run_artifacts/accel01_reuse_check"

python "$ACCEL_LANE/work_plan.py" \
  --profile ncp \
  --out "$ACCEL_RUN/plan.json"

python "$ACCEL_LANE/batch_worker.py" prepare \
  --plan "$ACCEL_RUN/plan.json" \
  --out "$ACCEL_RUN/prepared" \
  --case-store "run_artifacts/accel01_case_store" \
  --group-size auto
```

예상 상태는 `candidate_count=729, completed_count=729, pending_count=0, job_count=0, launched_jobs=0`이다. `prepared/no_work.json`이 생성되고 `prepared/manifest.json`은 생성되지 않는다. 이 경우 executor를 호출하지 않는다. 이미 보존된 동일 no-work receipt를 읽는 것만으로 충분한 재개라면 이 블록을 반복할 필요도 없다.

## 7. 사용자가 지정한 진짜 새 입력을 만드는 절차

이 절차는 **사용자가 다음 warm-LRS 연구 범위와 좌표·nsteps를 지정한 뒤** 적용한다. 고정 physics를 바꾸는 추가 필드는 현재 candidate schema에서 거부된다. full EoR나 다른 closure를 이 입력 형식으로 표현하지 않는다.

아래 JSON은 입력 형식 예시다. 실행 전에 사용자가 지정한 signed `(Sigma, Pi_m, Pi_r)` 값으로 확정해 `requested_signed_points.json`에 저장한다. 이미 사용한 smoke 값을 과학 결과를 늘리기 위해 다시 실행하지 않는다.

```json
[[0.00025, -0.00001, 0.00002]]
```

이 파일에서 exact case schema의 JSON과 CSV를 함께 만드는 예:

```bash
export ACCEL_LANE="research/rei_sigma_pi_acceleration_20261021"
export ACCEL_RUN="run_artifacts/accel01_next_user_scope"

python - <<'PY'
import csv
import json
import os
from pathlib import Path
import sys

lane = Path(os.environ["ACCEL_LANE"]).resolve()
run = Path(os.environ["ACCEL_RUN"])
sys.path.insert(0, str(lane))
import work_plan as wp

points = json.loads((run / "requested_signed_points.json").read_text())
cases = []
sign = lambda value: 0 if value == 0 else (1 if value > 0 else -1)
for index, point in enumerate(points):
    sigma, matter, radiation = map(float, point)
    case = {"case_id": f"custom_{index:04d}",
            "Sigma_half_requested": abs(sigma),
            "Pi_m_half_requested": abs(matter),
            "Pi_r_half_requested": abs(radiation),
            "shear_sign_requested": sign(sigma),
            "matter_stress_sign_requested": sign(matter),
            "radiation_stress_sign_requested": sign(radiation),
            "signed_Sigma_requested": sigma,
            "signed_Pi_m_requested": matter,
            "signed_Pi_r_requested": radiation,
            "signed_Pi_total_requested": matter + radiation,
            "nominal_cancellation": matter + radiation == 0}
    cases.append(wp.normalize_case(case))
cases = wp.validate_cases(cases)
run.mkdir(parents=True, exist_ok=True)
(run / "cases.json").write_text(json.dumps(cases, indent=2, sort_keys=True,
                                           allow_nan=False) + "\n")
with (run / "cases.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=sorted(wp.FIELDS))
    writer.writeheader()
    writer.writerows(cases)
print(json.dumps({"case_count": len(cases), "json": str(run / "cases.json"),
                  "csv": str(run / "cases.csv")}))
PY
```

JSON은 case object의 list이고 CSV에는 이 12개 case field만 둔다. 기존 aggregate의 full-result `cases.csv`를 candidate 입력으로 복사하지 않는다. signed total을 위처럼 같은 산술식에서 생성하면 수동 반올림으로 생기는 좌표 불일치를 피할 수 있다.

다음 `--nsteps 64`는 기존 계약의 기본값이다. 사용자가 다른 값을 지정했다면 그 값으로 바꾼다. 같은 좌표라도 nsteps가 달라지면 기존 완료 계산의 reuse 대상이 아니다.

```bash
python "$ACCEL_LANE/work_plan.py" \
  --cases "$ACCEL_RUN/cases.json" \
  --nsteps 64 \
  --profile ncp \
  --out "$ACCEL_RUN/plan.json"

python "$ACCEL_LANE/batch_worker.py" prepare \
  --plan "$ACCEL_RUN/plan.json" \
  --out "$ACCEL_RUN/prepared" \
  --case-store "run_artifacts/accel01_case_store" \
  --group-size auto
```

`--cases "$ACCEL_RUN/cases.csv"`도 지원한다. `work_plan.py`는 원래 seed mapping으로 positivity/domain을 검증하고, actual toolchain·full settings·scientific IDs를 plan에 기록한다. worker prepare는 그 내용을 다시 대조하므로 physics나 toolchain을 고친 뒤 SHA만 재계산해도 통과하지 않는다. auto grouping은 pending 수와 advisory worker 수에서 정하며 한 그룹은 최대16개다.

생성된 `plan.json`에서 `science_context_id`, 각 `pending[].science_id`, `pending[].science.parameters`, `pending[].science.toolchain`, completed/pending 수를 검토한다. 같은 machine에서 source가 바뀌거나 다른 host로 옮겼다면 기존 absolute-path group input을 실행하지 말고 새 plan/prepare를 생성한다. create-only 입력과 충돌하면 기존 증거를 덮어쓰지 않고 새 preparation directory를 사용한다. portable case store는 동일한 scientific/backend identity에 대해서 재사용할 수 있다.

## 8. 실제 pending 작업은 원 executor로 실행

이 명령은 pending이 존재하고 새 연구 범위가 확정된 경우, 실제 실행 host의 BASS checkout root에서 사용한다.

```bash
PILOT_LANE="research/rei_sigma_pi_pilot_20261021"

python "$PILOT_LANE/shared_executor.py" \
  "$ACCEL_RUN/prepared/manifest.json" \
  --scope "$ACCEL_RUN/execution" \
  --profile ncp \
  --max-workers 64 \
  --reserve-mb 1024 \
  --resource-wait-s 300 \
  --poll-s 0.5
```

executor가 실제 headroom을 재관측하고 worker numerical threads를1로 설정한다. profile의 64 CPU/128 GiB와 cgroup/affinity/실제 여유 중 적용 가능한 한도를 사용한다. resource wait가 끝났다고 전체 연구를 포기하지 말고 실제 executor summary와 pending 상태를 보존한 뒤 다음 가용 구간에서 이어간다. 기존 scope의 실패 attempt를 다시 시도할 때만 `--retry-failed`를 추가한다. 동일 scope의 다른 coordinator가 이미 작동 중이면 해당 coordinator의 증거를 확인하고 중복 실행하지 않는다. 다른 독립 scope나 세션의 작업은 계속 공존한다.

한 그룹은 원래 `split.run_case`를 그대로 사용한다. 성공 출력은 source/config/initial mapping, finite JSON, gates, nsteps/history, final row, history 기반 원 error reductions까지 검증한다. 실패 receipt와 checkpoint는 보존한다. case store의 손상은 명시적인 복구 대상으로 보고하고 새 결과로 조용히 대체하지 않는다.

**Aggregation 경계:** group result는 legacy 형식과 호환되지만 원래 `split_sweep.py aggregate`는 원729 signed grid와 case labels를 고정 검증한다. 새 custom grid나 다른 scientific input을 원729 aggregate/history/plots에 섞지 않는다. 새 사용자 연구 범위가 custom aggregate를 요구하면 별도의 expected-case contract와 provenance를 먼저 구현·검토한다.

## 9. 다음 단계 기록 방식

새 단계마다 DAG node의 실제 상태, 생성한 파일과 source identity, 검증 결과, 게시 상태, 백업 위치와 검증 상태를 함께 남긴다. 게시 성공과 백업 성공을 서로 대체하지 않는다. receipt가 없는 상태를 완료라고 기록하지 않는다. 게시할 산출물 commit과 그 commit을 가리키는 receipt commit을 구분하며 중앙 `delivery/` 기록을 갱신한다.

현재 구현은 최종25 tests 및 C9 PASS 뒤 freeze됐다. 문서·handoff를 읽었다는 이유만으로 이미 완료한729, 전체 test suite 또는 독립 review를 다시 시작하지 않는다. 실제 변경 의존성이 생겼을 때 필요한 범위만 검증한다. 아직 정해지지 않은 다음 연구 범위는 사용자에게서 받는다.

## 10. 다음 Codex 세션에 복사할 블록

```text
$physmath-research-loop ACCEL01 결과를 이어서 사용해줘.

branch: research/rei-sigma-pi-acceleration-20261021
경로: research/rei_sigma_pi_acceleration_20261021
BASS PR177: https://github.com/cosmosapjw-quantum/bass/pull/177
REI PR214: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/214

먼저 delivery/FINAL_PUBLICATION.json과 실제 delivery receipt들을 읽어 최종 source/publication/backup commit과 상태를 확인해줘. 이어서 DAG.json, REPORT_KO.md, CODEX_HANDOFF.md, evidence/VERIFICATION.json, evidence/INDEPENDENT_REVIEW.json, evidence/RUNTIME_CURRENT.json을 읽어줘. receipt가 없는 단계의 완료를 가정하지 마.

기존 warm conditional non-tilted LRS Bianchi I split729는 729 cases, 243 PASS groups, missing 0, history 47,385행으로 완료돼 있어. matter와 radiation의 pi_ab를 독립적으로 다루며 total은 signed 성분을 합한 뒤 norm을 취해. a=.1999→.2이고 full EoR, 일반 non-LRS, full Q^a, 수렴 입증은 별도 남은 범위야.

최적화는 exact-bit per-model massive moment cache, portable completed-case identity, pending-only planner, 원 shared_executor와 per-case atomic store 연결이야. 기본729 plan은 pending 0→no_work이고 job을 실행하지 않아. 최종25 targeted tests PASS, C9 한 차례29 guard probes PASS이며 새 custom case 하나의 실제2-step 연결 검산이 있어. 상세 benchmark 0, 이전729 full rerun 0을 유지하고 수렴이나 속도 배수로 해석하지 마.

NCP 64 CPU/128 GiB는 target이고 현재 NCP 자원은 UNOBSERVED야. Desktop Commander monthly usage paused와 local key absent가 기록돼 있어. sandbox 한도는8 CPU/8 GiB, 마지막08:04 UTC headroom은7 CPU와 약6.72 GiB(1 GiB reserve 후 약5.72 GiB)였어. 실제 실행 시 재관측하고 타 세션을 중지하지 말고 headroom 안에서 공존해줘.

내가 다음에 지정하는 연구 범위에 집중해줘. 새 입력은 현재 case schema의 JSON/CSV에서 plan과 scientific identity를 새로 만들고 prepare한 뒤 원 shared_executor.py --profile ncp --max-workers 64 --reserve-mb 1024로 연결해. 새 custom 결과를 고정 grid인 원729 aggregate에 섞지 마. 임의의 full EoR·수렴·affine 근사 확대나 상세 benchmark를 시작하지 마.

각 새 단계에서 실제 백업·게시·DAG 상태를 함께 남겨줘.
```
