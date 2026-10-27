# Phase A 구현 인계 — 실행 전

## 고정한 범위와 실행 상태

`CODING_CONTRACT_PHASE_A.md` 최종 SHA256은 `8393803be80a7ad7e4d9b0e728362da8ab32d63783c0ca3a1c3190de30ad4647`이다. 새 과학 실행은 아직 0회다. S0에 게시하는 입력·계약·survey snapshot은 변경하지 않았으며, 여기에 설명하는 신규 code 파일은 그 S0 manifest에 포함되지 않은 구현 준비다. `inputs/EXECUTION_FREEZE_PHASE_A_DRAFT.json`은 실행 준비용 초안이며 root의 실제 S0 게시·Drive/Dropbox ACK·Phase A 실행 지시가 오기 전에는 실행 freeze를 해제하지 않는다.

Phase A의 단일 subprocess가 새 diffusion bin100/179 × 두 knot의 네 역산, 독립 70자리 비교, 원 C 계수·operator 재구성, 원 snapshot holdout 비교, effective Maxwellian energy moment와 필요한 좁은 controls를 함께 수행한다. 이전 12개 inverse, finite photon 결과 프로그램, native history solver, B3i consume, 그림은 실행하지 않는다.

## 파일과 자료 경계

| 파일 | 구현 역할 |
|---|---|
| `code/native.py` | 원 table 순서·정규화·cubic 보간·diffusion·block/source 및 채널 전사, Thomas 소거 |
| `code/diffusion_inverse.py` | 이전에 검토된 scalar F/inverse helper만 재사용, 새 네 역산, 독립 70자리 bisection, assumed32ulp 구간 |
| `code/energy.py` | 고정 TR 편미분, 독립 70자리 polynomial differentiation, successful effective channel energy closure |
| `code/phase_a.py` | 하나의 controls+actual 실행, 중간 결과 보존, 계산 후 holdout 개방, 고정 기준별 readout |
| `code/metered.py` | 새 combined60 CPU/180 wall/768MiB/1thread guard와 누적 ledger, 자동 재실행 거부 |

입력 JSON의 shortest-roundtrip float를 실제 binary64 값으로 읽는다. x1s·TR·nH·H와 ys/yp는 이미 완료된 inverse 값을 사용한다. 새 네 trace 역산을 모두 먼저 보존한다. 두 bin과 `history.c::rec_Tmss`의 상대차가 실제로 2e-8 이내인 경우에만 원 steady formula의 Tm으로 downstream 계수를 계산한다. 네 trace Tm 자체는 그대로 유지한다. 이는 새 source-reconstruction 선택이며 기록되지 않은 과거의 전체 branch history를 증명하지 않는다.

`inputs/validation_only/RIGHT_NATIVE_SNAPSHOT_5127.csv`는 두 endpoint 구성과 결과 파일 저장 후에만 연다. 새 계수·행렬·energy moment의 입력으로 읽지 않는다. 원 source witness 안의 holdout 설명도 값 공급에 사용하지 않는다. holdout snapshot이 제공하지 않은 별도 물리 donor나 열 출력은 생성했다고 주장하지 않는다.

311 virtual unknowns는 복사된 원 radiation variables다. 원 source의 x1s=1−xHII 및 이 시대 xe=xHII convention을 따른다. 상수·switch·nH cm^-3·two-photon sequential normalization·small-tau arithmetic을 유지한다. two-photon 채널에는 diffusion 전 coupling을 사용하여 별도 core diffusion과 중복 계산하지 않는다.

## 명령과 환경

작업 디렉터리는 이 unit root다. root ACK와 현재 HEAD/AGENTS/parallel readback이 저장되고 final execution freeze가 승인된 뒤의 명령은 다음과 같다.

```sh
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python code/metered.py phase_a
```

`PYTHONPATH=/workspace/scratch/2a7ffd1a5e61/runtime_deps`와 OPENBLAS/OMP/MKL/NUMEXPR thread=1, PYTHONDONTWRITEBYTECODE=1을 wrapper가 child에 설정한다. 이전 실제 관측 환경은 Python3.12.14, numpy2.3.5, mpmath1.3.0이다. 이번 준비에서 새 설치나 import 테스트는 하지 않았다. matplotlib3.10.8은 나중에 별도로 고정할 saved-result-only plot의 기존 관측 버전이며 Phase A 의존성이 아니다. 정형 requirements에 기존 확정 버전을 기록했다. 원 35MB NPZ/history 재다운로드나 원 native exporter 재실행은 필요하지 않다.

모델 요청 기록은 gpt-6.1-sol, 실제 runtime model은 노출되지 않아 null이다. 이것은 과거 요청과 실제 관측을 분리하는 기록이며 모델 동일성 추정이 아니다.

## 보존·실패·예산

`results/SOURCE_OPERANDS.json`과 `results/PHASE_A_CHECKS.json`을 중간 단계마다 저장한다. 예외도 type/message와 부분 결과를 저장하며 stdout/stderr, exit code, exact command, child CPU/wall/RSS와 wrapper CPU는 `results/EXECUTION_LEDGER.jsonl`에 남는다. 고정 수치 기준 실패나 예외 시 root에 원자료를 반환하며 허용오차·closure를 자동 변경하지 않는다.

새 allocation60 CPU초·180 wall초는 Phase A, 별도로 고정할 Phase B, 한 번의 saved-only plot이 공유한다. 이 wrapper는 현재 Phase A만 받아들이므로 Phase B가 자동 시작되지 않는다. 이전 allocation은 closed이며 과거 unknown remainder는 null, 준비·모델·네트워크 비용도 측정하지 않은 값은 unknown으로 둔다. Phase A를 Phase B에서 재생성하지 않는다.

physical radii는 null이며 assumed32ulp propagation은 독립 구간의 수치 sensitivity 진단이다. 원 DAG27/88·증분0, 새 B3i0 경계를 그대로 유지한다. 수치 PASS 여부와 scientific admission은 root 및 독립 검토자의 몫이다.
