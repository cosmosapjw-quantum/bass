# ACCEL02 — NCP 실행용 Codex 인계

## 실행 범위와 현재 상태

이 문서는 이미 검토한 코드를 NCP의 기존 저장소에서 꺼내 실행하는 절차다.
현재 체크아웃의 추적 파일, 브랜치, 다른 세션의 작업을 바꾸지 않는다.
원격 브랜치를 fetch한 뒤 고정한 Git 객체에서 다음 세 경로만 새 실행 디렉터리로
`git archive` 한다. 이는 소스 내보내기이며 새 clone/worktree가 아니다.

- `research/rei_sigma_pi_pilot_20261021`
- `research/rei_sigma_pi_acceleration_20261021`
- `research/rei_sigma_pi_native_moments_20261021`

로컬 구현·검증은 완료됐고, fresh Astra C9 검토는 지적사항 없이 PASS다.
검증 당시 receipt의 `PENDING_ASTRA_REVIEW`는 그 시점의 실행 기록으로 보존하며,
후속 판단은 C9 기록과 현재 보고서를 따른다. 이번 범위는 기존96×32 적분의
반사대칭 쌍과 Neumaier 누적을 사용하는 massive three-moment backend다.
새16-node quadrature, solver/closure 변경, 전역 수렴, 측정된 가속비에 관한
주장은 없다. Native와 owner의 일치는 수치 허용오차로 판단하며 bitwise 일치를
주장하지 않는다. 모델 내부 exact-bit cache hit는 동일 tuple을 재사용한다.

기존64-step baseline729 결과와 그 gate는 그대로다. 기본 실행은 이729건의
완료 재사용이므로 pending0이다. 아래의 선택적 target check나 사용자가 제공한
새 사례만 pending 작업으로 실행한다. 새 grid나729건 재실행으로 자동 확대하지
않는다.

## 1. 기존 저장소 확인과 검토 객체의 소스 내보내기

기존 REI 저장소 안에서 Bash로 실행한다. 아래 고정 commit은 발행 담당자가
검토된 Stage B REI commit으로 치환한 값이다. commit 확인에 실패하면 현재
브랜치나 다른 commit으로 대체하지 말고 해당 식별자를 확인한다. 이 고정 객체는
REI PR215의 검토된 Stage B 소스다. 대응 BASS PR178 소스 commit은
`7fe0e25a28c0e48110c522378e203ffb934cc504`다.

```bash
set -euo pipefail
accel02_checkout="$(git rev-parse --show-toplevel)"
accel02_branch='research/rei-sigma-pi-native-moments-20261021'
accel02_commit='231df3ab717dbc112f63b77953f64def08e9bcb5'
accel02_run_root="$(mktemp -d /tmp/rei-accel02-ncp-XXXXXXXX)"
accel02_source="$accel02_run_root/source"
mkdir -p "$accel02_source" "$accel02_run_root/intake"

git -C "$accel02_checkout" status --short --branch | tee "$accel02_run_root/intake/checkout-status-before.txt"
git -C "$accel02_checkout" rev-parse HEAD | tee "$accel02_run_root/intake/checkout-head.txt"
git -C "$accel02_checkout" remote get-url origin | tee "$accel02_run_root/intake/origin.txt"
git -C "$accel02_checkout" fetch origin "$accel02_branch"
git -C "$accel02_checkout" cat-file -t "$accel02_commit"
git -C "$accel02_checkout" merge-base --is-ancestor "$accel02_commit" FETCH_HEAD
git -C "$accel02_checkout" show --no-patch --format=fuller "$accel02_commit" > "$accel02_run_root/intake/pinned-commit.txt"
git -C "$accel02_checkout" archive --format=tar "$accel02_commit" -- \
  research/rei_sigma_pi_pilot_20261021 \
  research/rei_sigma_pi_acceleration_20261021 \
  research/rei_sigma_pi_native_moments_20261021 | tar -xf - -C "$accel02_source"
git -C "$accel02_checkout" status --short --branch > "$accel02_run_root/intake/checkout-status-after.txt"

cd "$accel02_source"
accel02_lane="$accel02_source/research/rei_sigma_pi_native_moments_20261021"
accel02_executor="$accel02_source/research/rei_sigma_pi_pilot_20261021/shared_executor.py"
printf 'ACCEL02 run root: %s\n' "$accel02_run_root"
```

기존 dirty/untracked 파일은 그대로 둔다. `git checkout`, `git switch`, reset,
stash, clean, 별도 clone/worktree, 다른 프로세스의 종료는 필요하지 않다.
소스는 export 디렉터리에서 읽고 build/plan/case-store/scope는 아래처럼
`accel02_run_root`에 쓴다. commit된 `evidence/`에는 실행 결과를 쓰지 않는다.

## 2. 실행 환경과 자원 정책

기존 NumPy/SciPy 환경과 C++17 compiler를 사용한다. 새 환경 설치나 bootstrap은
이 작업의 전제가 아니다. 수치 라이브러리 thread는 모든 실행에서1로 고정한다.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export RAYON_NUM_THREADS=1 REI_TRANSPORT_THREADS=1
python --version > "$accel02_run_root/intake/python-version.txt"
if command -v g++ >/dev/null 2>&1; then
  g++ --version > "$accel02_run_root/intake/compiler-version.txt"
fi
```

NCP의64CPU/128GiB는 자원 상한이다.64 worker를 예약하거나 항상64개를 띄우라는
뜻이 아니다. 기존 `shared_executor.py --profile ncp`가 실제 CPU idle/quota와
메모리 여유를 launch 시점마다 다시 관측해 입장을 결정한다. 작은 target check는
`--max-workers 2`, 명시적으로 제공된 새 production 사례는 `--max-workers 64`를
상한으로 사용한다. 다른 세션의 부하 때문에 그 프로세스를 중지하거나 종료하지
않는다. 자원 대기로 실행이 끝나지 않으면 executor의 receipt와 상태를 보존한 뒤
같은 manifest/scope로 재개한다.

## 3. 기본 경로: 완료729건을 재사용하고 끝내기

이 경로는 native compile, library load, job 실행이 필요 없다.

```bash
python "$accel02_lane/native_worker.py" plan \
  --profile ncp \
  --out "$accel02_run_root/default-plan.json"
python "$accel02_lane/native_worker.py" prepare \
  --plan "$accel02_run_root/default-plan.json" \
  --out "$accel02_run_root/default-prepared" \
  --case-store "$accel02_run_root/default-case-store"
cat "$accel02_run_root/default-prepared/no_work.json"
```

예상 상태는 `REUSED_ALL`, `completed_count=729`, `pending_count=0`, `jobs=0`,
`launched_jobs=0`이다. `manifest.json`이 없으면 executor를 실행하지 않는다.
이것이 정상 완료이며 library가 없어도 성립한다. 새 pending이 요청되지 않았다면
여기에서 실행을 끝낸다.

## 4. 선택 경로: NCP target build와 제공된5사례의 작은 확인

NCP target에서 실제 build와 pending 실행을 확인할 때만 이 절을 선택한다.
이미 제공된 `CUSTOM_CASES.json`의5사례, 각2-step만 사용한다. 기존729건의
64-step 결과를 대체하지 않는다.140점 kernel matrix나 전체 unit suite를 다시
실행할 필요는 없다.

먼저 plan을 만든 뒤 pending이 있을 때만 compile/prepare/execute 한다.

```bash
python "$accel02_lane/native_worker.py" plan \
  --cases "$accel02_lane/evidence/CUSTOM_CASES.json" \
  --nsteps 2 --group-size 1 --profile ncp \
  --out "$accel02_run_root/small-plan.json"
accel02_small_pending="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["pending_count"])' "$accel02_run_root/small-plan.json")"
if [ "$accel02_small_pending" -gt 0 ]; then
  python "$accel02_lane/build_native.py" \
    --out "$accel02_run_root/native-build" \
    > "$accel02_run_root/target-build.json"
  python "$accel02_lane/native_worker.py" prepare \
    --plan "$accel02_run_root/small-plan.json" \
    --out "$accel02_run_root/small-prepared" \
    --case-store "$accel02_run_root/small-case-store" \
    --group-size 1 --build-dir "$accel02_run_root/native-build"
  if [ -f "$accel02_run_root/small-prepared/manifest.json" ]; then
    python "$accel02_executor" "$accel02_run_root/small-prepared/manifest.json" \
      --scope "$accel02_run_root/small-scope" --profile ncp --max-workers 2 \
      --resource-wait-s 300 --poll-s 0.5 \
      > "$accel02_run_root/small-executor-return.json"
  fi
else
  python "$accel02_lane/native_worker.py" prepare \
    --plan "$accel02_run_root/small-plan.json" \
    --out "$accel02_run_root/small-prepared" \
    --case-store "$accel02_run_root/small-case-store"
fi
```

build는 명시적으로 한 번 수행하며 prepare나 worker가 자동 compile하지 않는다.
build receipt는 compiler/version, 필수 flags, source hash, library hash,
platform을 기록한다. 다른 target의 binary나 build receipt로 인해 backend/source
ID가 로컬 기록과 달라도 그 자체는 과학적 FAIL이 아니다. NCP의 실제 build identity를
별도로 저장하고 출력은 gate와 수치로 판정한다. stale build/source가 거부되면
에러에 나온 rebuild 명령을 따른다. 다른 backend로 조용히 대체하지 않는다.

## 5. 다른 선택 경로: 명시적으로 제공된 새 사례를64-step으로 실행

사용자가 새로운 case JSON/CSV를 제공한 경우에만 이 절을 사용한다.
`--cases`는 기존 planner의 완전한 signed-case schema에 맞는 파일을 받는다.
제공된 사례만 다루며 grid 생성이나 자동 sweep 확대는 하지 않는다. 원래729건과
같은 좌표의64-step 사례는 완료 재사용되고 새 pending만 실행한다.
case 이름, 입력, nsteps, science ID, backend ID의 구분을 유지한다.

```bash
accel02_new_cases='/absolute/path/to/provided-new-cases.json'
python "$accel02_lane/native_worker.py" plan \
  --cases "$accel02_new_cases" --nsteps 64 --group-size 3 --profile ncp \
  --out "$accel02_run_root/new-plan.json"
accel02_new_pending="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["pending_count"])' "$accel02_run_root/new-plan.json")"
if [ "$accel02_new_pending" -gt 0 ]; then
  if [ ! -f "$accel02_run_root/native-build/build_receipt.json" ]; then
    python "$accel02_lane/build_native.py" \
      --out "$accel02_run_root/native-build" \
      > "$accel02_run_root/target-build.json"
  fi
  python "$accel02_lane/native_worker.py" prepare \
    --plan "$accel02_run_root/new-plan.json" \
    --out "$accel02_run_root/new-prepared" \
    --case-store "$accel02_run_root/new-case-store" \
    --group-size auto --build-dir "$accel02_run_root/native-build"
  if [ -f "$accel02_run_root/new-prepared/manifest.json" ]; then
    python "$accel02_executor" "$accel02_run_root/new-prepared/manifest.json" \
      --scope "$accel02_run_root/new-scope" --profile ncp --max-workers 64 \
      --resource-wait-s 300 --poll-s 0.5 \
      > "$accel02_run_root/new-executor-return.json"
  fi
else
  python "$accel02_lane/native_worker.py" prepare \
    --plan "$accel02_run_root/new-plan.json" \
    --out "$accel02_run_root/new-prepared" \
    --case-store "$accel02_run_root/new-case-store"
  cat "$accel02_run_root/new-prepared/no_work.json"
fi
```

## 6. 재개와 결과 반환

executor를 재개할 때는 해당 실행에서 사용한 같은 manifest와 scope를 지정한다.
성공한 job의 receipt는 재사용되며, case store는 case 단위 lock과 성공 기록으로
중복 solve를 막는다. 실패한 job을 재시도할 필요가 있을 때만 원래 명령에
`--retry-failed`를 추가한다. 결과를 숨기기 위해 scope/case store를 지우지 않는다.
물리 gate 실패, 알 수 없는 input/source identity, 불명확한 허용오차,
solver/closure 변경 필요가 생기면 raw 실패 기록을 보존하고 Astra controller에게
반환한다. 허용오차를 넓히거나 signed stress를 zero로 clip하지 않는다.

결과를 반환할 때는 다음을 run root와 함께 전달한다.

- pinned commit과 실행 전후 checkout status.
- plan, no-work receipt 또는 manifest, target build receipt와 실제 backend/source ID.
- executor execution policy, resource snapshot, job/attempt receipt, stdout/stderr, case 결과.
- pending/completed/실패 건수, 사용한 scope와 case-store, 다음에 실행할 구체적 명령.

NCP 결과의 과학적 admission은 Astra가 수행한다. 반환 후 controller가
DAG/loop/report의 해당 node에 증거, 현재 publication/backup checkpoint,
다음 실행 전이를 기록한다. run root는 임시 영역이므로 반환된 raw 결과를 요청된
저장소에 백업하고 provider acknowledgement를 받은 뒤 완료를 기록한다.
제출 사실만으로 backup 완료를 선언하지 않는다. NCP 실행으로 기존 baseline729나
로컬 검증 raw를 덮어쓰지 않는다.

## 기존 증거 요약

로컬에서 실행한 범위는 compile1회, kernel140점, 미분 identity3점,
original/native 각5개의2-step 궤적, 추가 native worker1개와 같은 case의 재사용1회,
기존 worker unit test9개다. 모두 동결 기준을 충족했다. 최대 kernel 오차는
`3.0017696087628955e-16`(J0로 정규화, 기준`64 eps64`), 최대 미분 residual은
`3.730718793634552e-12`(기준`2e-9`)였다. 각 궤적에서 기존8 gate를 유지했다.
benchmark와 원래729건의 재실행은 하지 않았다.

로컬 native backend/source ID는
`b0508de09a21c9da3ef5564e2cb63359d6263d2e68b2527b12971ef7b2ff6845`,
science-context ID는
`f5ab253bfd65a3af5b62dcc236cddb18e702b368b7e87e6213943617c1aab398`이다.
executor의 requested model은`gpt-6.1-sol`, observed runtime model은 telemetry가
제공되지 않아 null이다. requested identity를 관측 identity로 취급하지 않았다.

물리 범위는 비경사 LRS Bianchi I, 독립 matter/radiation P2 seed, warm 조건 구간
`a=0.1999..0.2`, L=8, source grid8×8, massive fraction0.1, mass/T=30이다.
full EoR, 일반 non-LRS/full Q^a, 전역 정확도·수렴, 속도 향상 주장으로 확장하지 않는다.


## Final delivery status / 최종 전달 상태

ACCEL02의 과학·구현·검토·인계는 `SCOPED_COMPLETE`다. Stage C 본문은
BASS `f94bad85fc913a5be7478251bc85457e6fafdb98`,
REI `369fd5007f7236e2bbb22e1bbe8ff0f1ceee2d5c` content commit에 게시됐다.
기존 Stage B code pin과 고정 과학 계약은 그대로 유지한다.

Dropbox의 5,514,078-byte Stage C ZIP을 **한 번의 전체 GET**으로 내려받아
size·SHA256·Dropbox block hash·ZIP CRC·263개 exact member를 모두 확인했다.
실제 영수증은 `delivery/STAGEC_PUBLICATION.json`, `STAGEC_BACKUP.json`,
`STAGEC_BACKUP_VERIFIED.json`, `FINAL_PUBLICATION.json`에 있다.
Stage A/B는 각각 provider object·size 확인이며, 전체 GET 검증은 Stage C에
한 번 수행한 것으로 구분한다.

불변 ZIP은 자체 provider ACK보다 먼저 만들어졌다. 최종 영수증과 이 상태
보충은 뒤따르는 Git closeout commit에 기록한다. ZIP을 재생성하거나 자기
hash를 재귀적으로 넣지 않는다. 최종 영수증의 Git commit은 이 파일을 포함하는 commit으로 확인한다.
위 content commit은 과학·인계 본문의 게시점이며 실행 코드 pin과 구분한다.

남은 NCP target-local compile·자원 확인·명시된 pending 실행은 별도 후속
작업이다. 이번 단위의 실패나 미완료 과학 검증으로 계산하지 않는다.
