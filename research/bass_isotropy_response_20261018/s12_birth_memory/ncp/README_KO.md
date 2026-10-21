# S12 NCP 실행·보존 도구

이 디렉터리는 새 S12의 고정 job DAG를 실행하고 결과를 보존하는 Python 표준 라이브러리 도구다. 기존 S9/S10/S11 캠페인을 재실행하지 않는다. 과학식, birth weights, angular/cohort reduction 순서는 여기서 변경하지 않는다. 실제 과학 job 목록과 입력은 부모가 고정하는 manifest가 소유한다.

## 사용자 지정 SSH 접속

현재 접속 계약은 [NCP_ACCESS_CONTRACT.json](../../NCP_ACCESS_CONTRACT.json)이며 [Codex 전체 handoff](../../CODEX_HANDOFF_KO.md)를 함께 읽는다.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

이 키는 SSH를 실행하는 호스트의 기존 로컬 파일이다. 접속 상태는 `SSH_AUTHORIZED_NOT_TESTED`, 실제 NCP job은 `NOT_RUN`이다. 이번 문서 변경은 연결·컴파일·실행을 하지 않았다. 지정 SSH로 접속한 담당자가 먼저 실제 host/CPU quota/RAM/disk/owner 작업과 기존 receipt를 read-only로 확인한다. 과거 Desktop Commander monthly quota/no-retry는 해당 서비스에만 적용하며 별도로 승인된 이 SSH 경로를 금지하지 않는다. launcher와 고정 source/input/binding은 변경하지 않았다.

## 최종 실행 입구와 고정된17job

실행 입구는 `launch.py`다. `JOB_TEMPLATE.json`에는 build1개, 새 extended Rust history14개,64개 고정 pack의 직렬/병렬 비교1개, ensemble 판정1개가 들어 있다. `inputs/`의81개 파일은 이미 Git에 게시한 고정 입력이며, 생성 시 solver를 호출하지 않았다. 입력이 준비됐다는 사실은 extended history가 통과했다는 뜻이 아니다. 실제 NCP 실행은 현재 `NOT_RUN`이다.

`SCIENCE_BINDING.json`은 Rust 과학 source `f4cd0d53760783e6a58c3b0a98c64311ca489d28`의15개 불변 파일을 묶는다. `DELIVERY_BINDING.json`은 별도 C8 source commit의 launcher·resource·집계기·고정 입력을 묶으며, 변경되는 DAG·문서·결과는 포함하지 않는다. 현재 배송 HEAD가 과학 source commit과 같아야 한다는 잘못된 조건을 두지 않는다. 각 binding의 actual bytes/SHA256/Git blob을 먼저 확인한다.

실행 주체인 Codex/NCP 담당자는 검증된 checkout과 별도의 work 디렉터리를 같은4GiB 측정 범위 아래에 둔다. 다음은 담당자가 실제 경로를 선택해 수행할 명령 형식이며, 사용자에게 선행 명령을 요구하는 절차가 아니다.

```bash
python3 REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/launch.py \
  --repo REPO \
  --template REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/JOB_TEMPLATE.json \
  --binding REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/SCIENCE_BINDING.json \
  --delivery-binding REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/DELIVERY_BINDING.json \
  --work-dir WORK --disk-root DISK_SCOPE --profile ncp
```

`REPO`와 `WORK`는 `DISK_SCOPE` 아래의 서로 다른 디렉터리다. launcher가 Rust1.94.1을 확인하고, 없으면 SHA256으로 고정한 공식 배포본에서 private toolchain의 필요한 regular files만 추출한다. 전역 toolchain 또는 owner 파일을 바꾸지 않는다. 기존 compiler를 명시하려면 `--rustc`와 `--cargo`의 실제 경로를 함께 전달할 수 있다. 해당 executable의 버전과 bytes identity만 주장하며 공식 archive와 같다고 추정하지 않는다. `--preflight-only`는 자원과 toolchain을 관측하고 proposal만 생성하며 실제 build/history를 실행하거나 최초 worker 폭을 봉인하지 않는다.

첫 실제 실행은 `WORK/JOB_MANIFEST.json`을 create-only로 봉인한다. 이후 같은 명령은 **처음의 자원 관측값으로 같은 worker 폭과 job identity를 재구성**한다. 현재 owner load가 달라져도 완료 job의 identity를 바꾸지 않는다. 현재 가용 자원이 부족하면 실행을 보류한다. source/input/toolchain/경로가 바뀌면 명시적으로 거절하며 기존 PASS를 새 입력의 결과로 재사용하지 않는다.

`aggregate.py`는14개 실제 history의 STARTED→dependency→build→upstream178파일→binary→input→stdout→assessment→outer receipt를 확인한다. 11개 full case의 과학 PASS와3개 omission control의 구조 PASS/물리 FAIL을 구분한 뒤 FD/Richardson·driver·baseline·gauge·omission을 판정한다. `AGGREGATE_INTERFACE_KO.md`가 정확한 CLI와 판정 scope를 설명한다. 이는 실제 native/reactive finite-bin closure 판정기가 아니다.

`verify_c8.py`의64CPU/128GiB는 **명시적 synthetic resource fixture**다. 실제 sandbox에서 실행하는 것은 두 version probe와 금지 profile 거절1회다. `verify_aggregate.py`는 완료한 짧은 history bytes의 배열 연산과 입력 거부를 확인한다. 어떤 검증도 실제 NCP64 실행이나 production 전체 receipt chain 통과로 쓰지 않는다. 실제 receipt는 상위 `evidence/`에 따로 보존한다.

### 실행 목록에서 제외한 원 native case

기존 S8 `b9_n64_P2P4`16birth의 고정 support는 birth13부터 양의 P24 해가 기존 tolerance에서도 불가능하다. 원 birth11 precision repair와 별개의 obstruction이다. `JOB_TEMPLATE.json`의 `pending_exclusions`에 exact certificate SHA256과 observer source를 기록했다. `native_followup/run.py`는 archival verify/compile-only만 허용하고 full history를 거절한다. 이를 실행하기 위해 weights·support·tolerance를 즉석에서 바꾸지 않는다. 실제 MD14/shared-Q 및 evolving reactive full finite-bin도 필요한 물리 입력이 없으므로 queue에 넣지 않는다.

## 파일과 실행 경계

- `resources.py`: Linux affinity, cgroup v1/v2 CPU/RAM 상한, 현재 가용 RAM, 현재 부하 및 할당 disk를 읽는다.
- `runner.py`: `preflight`와 `run`. 명시적 DAG, 자동 build dependency, process group, 원자적 receipt 및 exact-PASS resume를 구현한다.
- `bundle.py`: create-only ZIP과 다운로드 사본의 전체 bytes/SHA256/CRC/manifest 검증. 네트워크·provider mutation·과학 실행은 없다.
- `test_runner.py`: 작은 임시 helper만 실행하는 인프라 검증. 실제 BASS history 또는 NCP64 실행 결과가 아니다. 부모의 source freeze와 실행 허가 뒤에만 실행한다.

64CPU/128GiB는 `--profile ncp`의 요청 상한이다. 현재 host의 실제 자원이 이보다 작으면 낮춘다. `sandbox`는16worker/16GiB 상한이며, 실제8CPU/8GiB cgroup이면 그 한도를 따른다. job wall-time deadline은 기본 및 최대1800초다. 종료 처리 시간과 실제 elapsed를 receipt에 남긴다. 모든 profile의 측정 disk 범위는4GiB 이하로 제한한다. CPU 기존 부하는 관측 추정치이며 다른 owner의 future burst를 독점 예약했다고 주장하지 않는다. 기존 owner 작업에 signal을 보내지 않는다.

현재 실제 NCP64/128 실행은 별도 실행 receipt가 생기기 전까지 `NOT_RUN`이다. Desktop Commander quota, Browser 또는 Drive 우회 경로를 이 도구가 사용하지 않는다.

## Manifest 계약

최상위 필드는 다음과 같다.

| 필드 | 계약 |
|---|---|
| `schema` | `BASS_S12_JOB_MANIFEST_V1` |
| `scope` | `new_s12_birth_memory` |
| `allow_completed_campaign_replay` | 반드시 `false` |
| `source_files` | repo-relative path → 실제64자리 소문자 SHA256. launcher·resource code와 모든 실행 source를 포함할 것 |
| `reserve_cpus` | owner 여유분. 기본1, 음수 금지 |
| `reserve_ram_bytes` | owner 및 driver 여유분. 기본1GiB |
| `max_workers` | 1–64. profile·실제 affinity/quota·RAM·부하가 추가 제한 |
| `jobs` | 고정 job 배열. 중복 ID와 dependency cycle 금지 |

각 job의 필드:

| 필드 | 계약 |
|---|---|
| `id` | 안전한 고유 문자열 |
| `kind` | `build`, `new_rust_history`, `paired_finite_difference`, `matched_accuracy_performance`, `failed_native_b9_n64` 중 하나 |
| `needs` | 먼저 PASS 또는 검증된 exact-PASS가 필요한 job ID 목록 |
| `argv` | shell 없는 실제 인자 배열. `{repo}`, `{run}`, `{dep:job_id}`만 경로 치환 |
| `input_files` | repo-relative path → SHA256. non-build job에서는 비어 있을 수 없음 |
| `cpus` | 양의 정수. whole independent cases를 병렬 실행; ray reduction 분할용 아님 |
| `ram_bytes` | 양의 정수. own-job 예약 및 process group RSS 관측과 address-space 제한 |
| `timeout_s` | 0보다 크고1800 이하; 생략 시1800 |
| `output_budget_bytes` | artifact·로그·receipt를 포함한 job 출력 예약. 파일 크기 제한과 group output 감시 |
| `artifacts` | 새로운 attempt working directory에 생성할 상대 파일 경로 목록 |
| `accept` | `{artifact, pointer, equals}` 배열. scientific job에서는 필수. JSON pointer 값의 타입과 값이 정확히 일치해야 함 |
| `expected_exit` | 기본0. 의도한 negative control이면 명시한 실제 exit code와 acceptance를 함께 고정 |
| `env` | 선택 문자열 mapping. numerical thread 변수는 항상1이며2 이상 요청은 거절 |

예를 들어 build job은 `rustc`, 고정 source 경로, `-o`, `{run}/birth_memory`를 argv로 가지며 artifact는 `birth_memory`다. 후속 case argv의 첫 항목을 `{dep:build}/birth_memory`로 하고 `needs=["build"]`로 연결한다. 사전 사용자 build 명령이 필요하지 않다. 실제 compiler command와 source hashes는 고정 manifest에 넣는다.

실행 job은 `{run}` 아래에만 출력하도록 작성·검토해야 한다. launcher는 범용 OS 보안 sandbox가 아니다. source/input hash는 launch 전에 검증하며, source checkout의 owner 파일을 갱신하는 명령은 manifest에 넣지 않는다.

## 자원 admission과 resume

실제 CPU 상한은 profile, affinity, cgroup quota의 최솟값이다. 현재 host·cgroup CPU 관측에서 own group 사용량을 분리해 기존 부하를 남기고, own-job 예약 합계가 상한을 넘지 않도록 한다. 현재 가용 RAM에서 reserve 및 진행 중인 job의 아직 사용하지 않은 예약을 제외한다. disk는 고정 `--disk-root`의 allocated blocks로 측정하고 동시 출력 예약도 제외한다. 충분하지 않으면 새 job을 시작하지 않는다. 관측 부하는 독점적 시스템 예약을 뜻하지 않는다.

own-job CPU/RSS 집계는 정확한 소유 PGID의 구성원과 `/proc`의 PPID descendant tree를 함께 읽으므로, 감독 중인 wrapper가 만든 별도 session의 compiler/native child도 포함한다. 신호는 이 ancestry 추정치에 보내지 않는다. child가 관측 전에 reparent되면 ancestry가 사라질 수 있으므로 검토된 wrapper는 child 종료까지 감독하며, polling 값은 연속 peak 측정치가 아니다.

disk 보호는 시작 전 output 예약, 실행 중 allocated-block 관측, 파일별 `RLIMIT_FSIZE`를 함께 사용한다. 관측된4GiB 초과는 FAIL이며 이후 job을 시작하지 않는다. 이 도구가 filesystem quota를 설치하지는 않으므로 polling 사이의 순간적인 초과까지 차단하는 hard quota라고 주장하지 않는다.

실행은 새 `runs/<job_id>/<UTC_nonce>/`에만 기록한다. `STARTED.json`은 실제 command, source/input identity, CPU/RAM/timeout과 시작시각을 남긴다. `receipt.json`은 종료 후 임시 파일 fsync와 atomic link로 한 번만 생성한다. 기존 receipt나 이전 attempt는 덮어쓰지 않는다.

resume는 다음이 모두 맞는 **PASS만** 재사용한다: normalized job contract, source/input SHA256, 실행 파일 SHA256·realpath, single-thread environment, dependency identity 및 모든 artifact/log byte hash. FAIL, 미완료, command 변경, input 변경, artifact 손상은 skip 대상이 아니다. 새 attempt를 만들며 이전 실패를 남긴다. 미완료 dependency의 후속 job은 실행하지 않는다. 여러 launcher가 같은 run root를 동시에 사용하면 flock으로 두 번째 시작을 거절한다.

timeout·RAM/output 초과·driver interruption은 **이 launcher가 새 session으로 생성한 process group만** 종료한다. 정상 exit 뒤에도 살아 있는 child writer가 있으면 PASS로 승격하지 않는다. failed 또는 interrupted 결과도 bundle에 보존된다.

검토된 wrapper가 내부 child를 별도 session으로 만들면 wrapper 자신이 SIGTERM/SIGINT를 받아 그 child group을 정리하고 종료해야 한다. outer launcher의2초 정리 유예 안에 완료하도록 inner 정리 유예를1초 이하로 둔다. 임의 daemonization을 자동으로 회수하는 process supervisor라는 보장은 하지 않는다.

## 자동 실행과 전달 명령 형식

아래는 다음 실행 주체가 manifest의 실제 경로로 바인딩할 command 형태다. 사용자에게 선행 명령을 요구하는 절차가 아니다.

```text
python runner.py preflight --manifest JOBS.json --repo REPO --runs NEW_RUNS --disk-root DISK_SCOPE --profile ncp
python runner.py run --manifest JOBS.json --repo REPO --runs NEW_RUNS --disk-root DISK_SCOPE --profile ncp
python bundle.py create --manifest JOBS.json --repo REPO --runs NEW_RUNS --output NEW_RETURN.zip --disk-root DISK_SCOPE
python bundle.py verify --archive DOWNLOADED_RETURN.zip --sha256 SEALED_SHA256 --bytes SEALED_BYTES
```

`preflight`는 scientific process를 시작하지 않는다. `run`은 manifest의 build dependency부터 자동 실행한다. 고정 source/input과 자동 생성 command를 포함한 최종 NCP manifest는 별도 publication checkpoint가 소유한다.

bundle은 job manifest, 선언한 source/input, 모든 선택된 run receipt·로그·artifact를 포함한다. 봉인 archive의 자체 SHA256은 ZIP 바깥 `.receipt.json`에 기록한다. 원격 사본 검증은 caller가 보존한 archive SHA256과 bytes를 필수로 받아 전체 ZIP 및 각 payload를 확인한다. packaging PASS와 과학 PASS는 구별한다.
