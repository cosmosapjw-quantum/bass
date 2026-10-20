# S12 C8 저장 결과 집계기 인계

이 파일과 `ncp/aggregate.py`는 새 staging 산출물이다. 기존 R2, 과거 캠페인, 기존 repo 파일은 수정하지 않았다. 작성 중 집계기, observer, 적분기, projector, compiler를 실행하지 않았다. 구문은 AST로만 확인한다. 작성자가 구현한 코드이므로 독립 C9 승인으로 취급하지 않는다.

## CLI

```text
python /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/aggregate.py
  --repo /REPO
  --job-manifest /PATH/ACTUAL_JOB_MANIFEST.json
  --histories /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/inputs/HISTORIES.json
  --science-binding /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/SCIENCE_BINDING.json
  --preregistration /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/PREREGISTRATION.json
  --source-commit f4cd0d53760783e6a58c3b0a98c64311ca489d28
  --out /AGGREGATE_ATTEMPT
  --case p24_y0_full=/HISTORY_ATTEMPT
  ... 나머지 13개 고정 case
```

실제 job manifest의 argv는 문자열 배열이다. 각 case 인자는 `--case`, `p24_y0_full={dep:history_job_id}` 두 원소로 넣는다. case ID와 launcher job ID는 달라도 된다. `--job-manifest`는 모든 job을 포함한 실제 실행 manifest이고, 자기 해시를 `input_files`에 넣지 않는다. 그 파일의 실제 SHA256은 각 STARTED/receipt의 manifest SHA와 비교한다.

집계 job은 `kind=paired_finite_difference`, `needs`는 정확히 14개 history job이어야 한다. `{run}`의 `STARTED.json`이 생성된 상태에서 실행한다. 해당 STARTED의 dependency identity 및 artifact map과 실제 case attempt를 대조한다. case 경로는 14개 모두 달라야 한다. 완료한 14개 history의 binary와 build identity도 같아야 한다. 원본 attempt를 옮기거나 absolute path를 다시 쓴 자료는 이 실행 검증 경로에서 자동 승인하지 않는다.

권장 자원은 CPU 1, RAM 2 GiB, timeout 1800초 이하, output budget 128 MiB이다. 이 권장은 측정된 실행 시간이나 메모리 사용량이 아니다. stdlib assessor의 저장 결과 재평가 외에 새 과학 실행은 없다.

## 선언할 입력과 출력

전체 manifest의 `source_files`에 동결된 `assess_history.py`, `process_control.py`, `ncp/history_job.py`, `prepare.py`와 현재 `ncp/runner.py`, 새 `ncp/aggregate.py`를 반드시 포함한다. 네 동결 helper는 SCIENCE_BINDING의 f4 해시와 같아야 한다. 집계 job의 `input_files`는 HISTORIES.json, PREREGISTRATION.json, SCIENCE_BINDING.json의 실제 repo 상대 경로와 SHA256을 포함한다. 각 history job은 해당 고정 history input JSON을 `input_files`에 선언한다.

각 history job은 다음 8개를 artifacts에 선언한다. launcher가 따로 선언하는 `stdout.log`, `stderr.log`는 중복 기입하지 않는다.

- `INPUT.json`
- `HISTORY.json`
- `history.stdout`
- `history.stderr`
- `ASSESSMENT.json`
- `PROCESS.json`
- `RETURN.json`
- `BOUNDARY_CHECKPOINT.json`

각 history job은 단일 build job을 의존하며, build는 선행 dependency가 없는 직접 build여야 한다. Build artifacts는 실제 `prepare.py --work-dir` 아래의 `BUILD_RECEIPT.json`, `COMPILE_PROCESS.json`, `compile.stdout`, `compile.stderr`, `target/release/s12-history`를 포함한다. 예를 들어 work-dir가 `{run}/work`이면 모두 `work/` 접두사를 붙인다. build 작업 디렉터리의 실제 `client/s12_birth_memory/` source와 `client/s11_p246/rust/projector.rs`도 남아 있어야 한다. 별도의 build 산출물 정리는 집계 후 수행한다.

집계 job의 artifacts는 다음 7개다.

- `RETURN.json`
- `CHECKS.json`
- `EVIDENCE.json`
- `CASE_ASSESSMENTS.json`
- `FD_RICHARDSON.json`
- `CROSS_DRIVER.json`
- `OMISSION_CONTROLS.json`

accept는 `RETURN.json`의 `/status == PASS_NEW_EXTENDED_ENSEMBLE`를 선언한다. 실패는 exit 1과 status FAIL로 보존한다. 기존 위 7개 중 하나라도 이미 있으면 새 결과로 덮어쓰지 않는다. 선행 case 하나가 실패하면 나머지 읽을 수 있는 case의 검토를 계속하여 원인을 기록하되, ensemble 통과를 내리지 않는다.

## 고정 판정

14개 case, k16/n64, birth_end 0.8, x_end 1.2 및 49개 공통 출력 시각을 HISTORIES.json과 대조한다. 입력의 허용 차이는 GL birth rule, b0 gauge parameter, MF6 arm, baseline mode, 세 y0 FD 간격, 세 명시적 omission control뿐이다. old physical stock, donor law, event coordinates, 나머지 solver 설정은 바꾸지 않는다.

| 판정 | 고정 기준 |
|---|---:|
| full 11개 단독 history | source/process/구조/수치 gates 모두 통과 |
| omission 3개 | 완료 + 구조 통과; full physics pass는 false |
| MF6 vs clock7 state6 | scaled 최대 오차 ≤ 1e-9 |
| baseline vs fused state6 | scaled 최대 오차 ≤ 2e-13; 내부 numerical gate map 동일 |
| GL b0 gauge | 모든 observation에서 max(abs(Sh), abs(Sy), abs(Sb−1)) ≤ 1e-11 |
| FD 간격 | 1e-4, 5e-5, 2.5e-5 그대로 |
| fine Richardson h,b,y tangent | 최대 절대 오차 ≤ 1e-8 |
| finest raw FD | scaled 최대 오차 ≤ 1e-6 |
| 각 omission 효과 | max(abs(full−omitted)) > 10 × max(abs(full−fine Richardson)) |

scaled denominator는 `1 + max(abs(a), abs(b))`이며 모든 값과 denominator가 유한하고 denominator가 양수여야 한다. 전체 FD 배열, coarse/fine Richardson, 오차 배열, 각 control의 failed numerical check를 산출물에 보존한다. 원시 HISTORY/stdout, stdlib observer의 저장 재평가, process stderr의 completion binding/cardinality를 모두 대조한다. 통과와 실패를 기록한 뒤 모든 읽은 파일을 다시 해시하여 중간 변경 여부를 확인한다.

이 C8는 extended 독립 Python 적분, checkpoint resume, 실제 NCP64 하드웨어 확인, native full spectral history/continuum 수렴을 수행하거나 승인하지 않는다. 원래 S9/S10/S11 또는 완료한 S8 17개 case를 재실행하지 않는다. remote Git publication/readback은 root의 별도 배송 근거로 연결한다.


## C8 R3 후속 강화와 제한된 검증

`verify_build`는 고정 upstream manifest만 확인하는 데서 더 나아가, 실제 build 작업 디렉터리 `vigilode/`의 178개 소스 파일을 읽어 bytes/SHA256/Git blob을 모두 다시 확인한다. 이 검사는 기존 compiler/process receipt 검사를 대체하지 않는다. 파일은 수정하지 않고 집계 종료 때 unchanged readback에 포함한다.

`ncp/verify_aggregate.py`는 이미 완료한 **짧은 S12 14-case** 원자료를 재사용하여 새 집계기의 순수 배열 연산을 기존 FD·MF6·baseline·omission 수치와 비교한다. 현 extended 입력 manifest와 기존 upstream 파일을 확인하고 JSON 중복키/비유한수/shape/분모/중복 observation 거부도 검사한다. source/receipt를 가짜로 만들어 production 실행을 승인하지 않는다. 전체 launcher receipt chain, 실제 extended history 또는 NCP64 검증으로 해석하지 않는다. solver/projector/compiler/subprocess/network 호출은 모두 0이다. 구현 작성자의 검증이며 독립 C9가 아니다.

```text
python /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/verify_aggregate.py
  --aggregate /REPO/research/bass_isotropy_response_20261018/s12_birth_memory/ncp/aggregate.py
  --aggregate-sha256 FROZEN_PUBLISHED_AGGREGATE_SHA256
  --repo /REPO
  --short-dir /COMPLETED_SHORT_HISTORY_R2
  --upstream-root /EXISTING_SOURCE_BOUND_BUILD/vigilode
  --out /NEW_VERIFICATION_ATTEMPT
```

검증기 내부 한도는 AS 512 MiB, 출력 파일 32 MiB, 90초이다. 소스 게시 전 실행하지 않는다. 변경 이전 코드와 diff는 `revision_r3/`에 보존했다.
