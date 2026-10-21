# ACCEL03 — 저장 결과 분석·후속 실행용 Codex 인계

## 현재 완료 상태와 다음 행동

실제 NCP 5사례×2-step 실행은 이미 완료됐고, 변경하지 않은 ACCEL02 수치 기준으로
admit됐어. ACCEL03의 집계·진단·그림도 완료됐고, controller의 두 그림 표기 정정을
반영한 결과가 fresh 독립 심사에서 수용됐어. 지금 필요한 기본 행동은 아래의 기존 결과를 확인하는 것이야. NCP 궤적,
원 729건, kernel matrix, 기존 전체 test suite, benchmark를 다시 돌릴 요청은 없어.

- `results/ncp5/`: 5 expected, 5 successful pending, 0 missing, 실제 history 15행.
- `results/ncp5/plots/actual_samples_4ff69a0d5fef.png`: 실제 저장 시점 그림.
- `results/baseline729/`: 완료된 729건의 endpoint projection, history 0행.
- `results/baseline729/plots/endpoint_slice_caed0ccd4a58.png`: 정확한 signed Sigma=0 slice.
- 각 그림의 `source_points.csv`와 `plot_provenance.json`: 실제 점과 입력의 대응.

원 pilot의 729 cases/243 groups PASS/누락 0/history 47,385행이라는 완료 기록은
그대로야. 원 history 전체는 원 archive/index/hash/locator에 있고 이번 로컬
projection에 복원하지 않았어. Endpoint-only projection을 64-step history라고
표현하지 마. NCP 2-step 자료는 initial+evolved 2개, 총 3시점씩이야.

현재 작업 branch는 `research/rei-sigma-pi-sweep-analysis-20261021`, PR은
[BASS179](https://github.com/cosmosapjw-quantum/bass/pull/179)와
[REI217](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/217)이야.
검토된 Stage B의 대응 BASS 실행 소스 pin은 `b0ea16c9172c8b1553cbdb35cb03460160db1412`이야.
아래 REI pin도 실제 게시된 Stage B 값으로 확정했어. 이후 같은 branch의
Stage C 문서·delivery commit은 검토된 실행 코드를 바꾸지 않아.

## 1. 기존 저장소의 고정 Git 객체에서 네 lane 내보내기

기존 REI checkout 안에서 Bash로 실행해. 현재 branch를 checkout/switch하거나
새 clone/worktree를 만들지 않아. Fetch한 객체에서 네 경로만 고유 실행 폴더로
내보내므로 공유 checkout의 추적 파일과 다른 세션 작업을 바꾸지 않아.

```bash
set -euo pipefail
accel03_checkout="$(git rev-parse --show-toplevel)"
accel03_branch='research/rei-sigma-pi-sweep-analysis-20261021'
accel03_pin='39ae7c843ea2d1adf580aff44aebfdedea7e33aa'
accel03_run_root="$(mktemp -d /tmp/rei-accel03-analysis-XXXXXXXX)"
accel03_source="$accel03_run_root/source"
mkdir -p "$accel03_source"
git -C "$accel03_checkout" fetch origin "$accel03_branch"
git -C "$accel03_checkout" cat-file -t "$accel03_pin"
git -C "$accel03_checkout" merge-base --is-ancestor "$accel03_pin" FETCH_HEAD
git -C "$accel03_checkout" show --no-patch --format=fuller "$accel03_pin" > "$accel03_run_root/source-pin.txt"
git -C "$accel03_checkout" archive --format=tar "$accel03_pin" -- \
  research/rei_sigma_pi_pilot_20261021 \
  research/rei_sigma_pi_acceleration_20261021 \
  research/rei_sigma_pi_native_moments_20261021 \
  research/rei_sigma_pi_sweep_analysis_20261021 | tar -xf - -C "$accel03_source"
cd "$accel03_source"
accel03_lane="$accel03_source/research/rei_sigma_pi_sweep_analysis_20261021"
accel03_python="$(command -v python3)"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export RAYON_NUM_THREADS=1 REI_TRANSPORT_THREADS=1
printf 'ACCEL03 run root: %s\n' "$accel03_run_root"
```

실제 NCP 첫 실행에서는 `python` 명령이 exit127이었고 `/usr/bin/python3`로
복구했어. 위 명령은 사용 가능한 `python3`를 선택해. 기존 NumPy/Matplotlib/SciPy
환경을 사용하고 새 설치나 bootstrap을 전제로 하지 않아. 저장 결과 분석에는
native compiler/library가 필요 없어. 네 lane 외의 파일 상태를 덤프하거나 다른
프로세스를 종료할 필요도 없어. 고정 pin을 확인하지 못하면 임의의 다른 commit으로
대체하지 말고 해당 식별자를 확인해.

## 2. 선택 사항: 제공된 저장 fixture에서 분석만 다시 만들기

이미 만들어진 분석과 그림을 사용할 수 있으므로 이 절의 재생성은 선택 사항이야.
아래 명령은 ODE 실행·native build 없이 저장 파일만 읽어. 출력은 새 run root에
쓰고 commit된 `results/`와 원 증거는 덮어쓰지 않아.

```bash
"$accel03_python" "$accel03_lane/aggregate.py" \
  --plan "$accel03_lane/results/inputs/ncp5/small-plan.json" \
  --manifest "$accel03_lane/results/inputs/ncp5/small-prepared/manifest.json" \
  --scope "$accel03_lane/results/inputs/ncp5/small-scope" \
  --out "$accel03_run_root/ncp5-analysis"
"$accel03_python" "$accel03_lane/plot_sweep.py" \
  --aggregate "$accel03_run_root/ncp5-analysis" \
  --out "$accel03_run_root/ncp5-plots"
"$accel03_python" "$accel03_lane/aggregate.py" \
  --plan "$accel03_lane/results/inputs/ncp5/default-plan.json" \
  --out "$accel03_run_root/baseline729-analysis"
"$accel03_python" "$accel03_lane/plot_sweep.py" \
  --aggregate "$accel03_run_root/baseline729-analysis" \
  --signed-sigma 0 --out "$accel03_run_root/baseline729-plots"
```

`aggregate.py`는 `--plan`을 전체 예상 후보의 기준으로 삼고 pending-only manifest의
건수를 전체 분모로 쓰지 않아. `--scope`와 `--result`는 반복 지정할 수 있어.
Scope 경로는 기존 성공 receipt/hash 선택을 사용하며, `--result` 직접 import는
그 경로를 provenance에 별도로 기록해. Analyst의 Python/NumPy/SciPy version을
옛 결과의 수용 기준으로 강제하거나 `PreparedContext`를 만들지 않아.

결과는 `summary.json`, `cases.csv`, `history.csv`, `diagnostics.json`,
`provenance.json`이야. 누락 사례는 `PARTIAL`과 명시적인 ID로 남고 0으로 채우지
않아. 예상 밖 사례·충돌·잘못된 binding·step 수·원 gate 실패는 명시적으로 거절해.
그림은 이 출력만 읽어 실제 점과 저장 시점만 표시하고 source point table을 남겨.
`--signed-sigma`는 정확한 requested signed shear slice이며 가까운 값으로 대체하지 않아.

상쇄 진단은 signed 성분을 먼저 더하고 성분 규모로 산술 잔차를 판단해.
ZERO_COMPONENT_SCALE/EXACT_CANCELLATION의 정의되지 않는 비율·조건수는 null이야.
같은 source/backend/toolchain/context/nsteps/구간의 정확한 control이 없으면
control-subtracted response도 null이며 raw final-minus-initial과 구별해.

## 3. 나중에 제공되는 새 저장 결과의 분석

새 결과가 반환되면 실행 전에 먼저 기존 plan·manifest·receipt·science ID와
중복 여부를 확인해. 새로 제공된 실제 saved outputs가 있다면 다음 형식만
그 입력에 맞춰 사용해. 지금은 새 사례나 grid가 제공되지 않았으므로 이 절을
자동 실행하거나 사례 범위를 확대하지 않아.

```bash
accel03_return_plan='/absolute/path/to/provided-plan.json'
accel03_return_manifest='/absolute/path/to/provided-manifest.json'
accel03_return_scope='/absolute/path/to/provided-successful-scope'
"$accel03_python" "$accel03_lane/aggregate.py" \
  --plan "$accel03_return_plan" --manifest "$accel03_return_manifest" \
  --scope "$accel03_return_scope" --out "$accel03_run_root/new-analysis"
"$accel03_python" "$accel03_lane/plot_sweep.py" \
  --aggregate "$accel03_run_root/new-analysis" \
  --out "$accel03_run_root/new-plots"
```

manifest의 target 절대 경로를 analyst host에서 다시 실행하지 않아. 해당 plan과
실제 결과·receipt를 함께 보존해 portable 분석 경로를 사용해. 서로 다른 수치
cohort는 계속 구분하며 archived729를 모두 native 실행이라고 표시하지 않아.

## 4. 향후 명시적으로 승인된 새 pending 실행이 생길 때

현재 NCP 5사례는 완료됐어. ACCEL02 handoff의 NCP 실행 전제보다 이 최신 완료
상태를 우선해. 현재 요청은 재실행이 아니며 새 case 범위·nsteps는 사용자가 정해야 해.
그때의 순서는 다음과 같아.

1. 사용자가 제공한 case JSON/CSV만 `native_worker.py plan --cases ... --nsteps ...`
   으로 계획해. 기본729/64-step은 완료 재사용되어 pending0인 것이 정상이야.
2. pending0이면 `prepare`의 no-work receipt로 끝내. Manifest가 없으면 compiler나
   executor를 호출하지 않아.
3. 진짜 pending이 있을 때만 명시적인 target build를 하고 `prepare --build-dir ...`
   로 새 manifest를 만들어. 실제 build/library/backend identity를 따로 남겨.
4. 기존 `shared_executor.py MANIFEST --scope SCOPE --profile ncp --max-workers 64`
   를 사용해. 작은 확인은 `--max-workers 2`로 제한해.
5. 같은 plan·manifest와 성공 scope를 위 `aggregate.py`에 주고 `plot_sweep.py`로
   실제 저장 점만 그려. 원729 고정 aggregator에 custom/2-step 결과를 넣지 않아.

위 native plan/build/prepare의 상세 parser-compatible 예시는 ACCEL02
`CODEX_HANDOFF.md`를 참고하되, 저장 결과 분석의 `python3` 선택과 이 문서의
완료 상태·새 입력 범위를 우선해. 자동 grid 생성, benchmark, 원729 재실행은 없어.

`64 CPU/128 GiB`와 `--max-workers 64`는 상한이지 예약 수량이 아니야.
실제 affinity/quota/idle CPU/RAM과 pending job 수가 동시 dispatch를 제한하며,
기존 executor가 launch 시점마다 다시 관측해. 다른 job이 바쁘다는 이유만으로
다른 프로세스를 종료하거나 작업을 포기하지 말고 가용 자원에 맞춰 진행해.

확인된 자원 관측은 다음과 같아. Sandbox는 quota 8 CPU/8 GiB였어.
NCP의 2026-10-21 21:56:39–42 KST 저장 snapshot은 affinity 64 CPU,
total 125.78 GiB, available 약 80.20 GiB였어. 이 수치는 그 시점 관측값이며
현재 live 여유량은 이 대화에서 직접 관측하지 못했어.

## 5. 반환·후속 연구·checkpoint

다음 과학 범위는 아직 사용자가 정해야 해. Full EoR, 일반 non-LRS/full Q^a,
시간·radial·angular 수렴, measured speedup은 이번 수용 범위가 아니야.
Massive fixed-weight response identity는 radiation collision/emission/UV 항을
대체하지 않아. 새 범위가 없으면 완료된 단위를 다시 심사하거나 test matrix를
반복하지 말고 기존 결과를 재사용해.

새 반환 자료가 생기면 입력 identity·누락·cohort·실제 점을 먼저 검토하고,
각 단계의 증거/DAG node/실제 publication commit/provider backup ACK를 갱신해.
제출 사실만으로 backup 완료를 선언하지 않아. Conversation 검색 호출이 이
세션에서 unavailable을 반환했으므로 접근하지 못한 대화까지 전수 확인했다는 주장은
할 수 없어. 제공된 반환 자료와 접근 가능한 Git/backup 증거의 범위를 명시해.

정확한 최종 publication/backup 상태는 이 branch의 `delivery/`와 현재
`DAG.json`, `LOOP_RECORD.json`을 읽어 확인해. Stage B의 증거 생성 당시
`PENDING_INDEPENDENT_REVIEW`는 보존된 시점 기록이고, 이후 판정은
`evidence/INDEPENDENT_REVIEW.json`과 현재 scoped decision을 따른다.
