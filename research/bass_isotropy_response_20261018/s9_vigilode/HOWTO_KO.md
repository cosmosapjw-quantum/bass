# S9 실행 기록과 명시적 재현용 HOWTO

> **현재 상태(2026-10-20): S9 고정 8개 history는 이미 8/8 완료, 140개 gate assertion PASS이며 독립 dual 검토는 PASS_SCOPED다. 140은 독립 테스트 수가 아니다. NCP 재실행 의무는 없다. 아래 build/campaign 명령은 명시적인 재현 연구에만 사용하는 역사적 절차이고 다음 작업 지시가 아니다. 다음 구현 범위는 [Codex/NCP 인계](../CODEX_HANDOFF_KO.md)를 따른다.**

실제 실행 source는 `4b30957cb008aad8019bb1a673937fc67bd017e8`, tree는 `8e4abf3820d06bae6cbec307e4f69de74195d14b`다. 현재 fresh build는 [PREPARATION_RETURN](../evidence_s9/resume_20261020/runtime/PREPARATION_RETURN.json), 실제 8개 결과는 [CAMPAIGN_RETURN](../evidence_s9/run_20261020_r1/CAMPAIGN_RETURN.json), 독립 검토는 [DUAL_REVIEW_RECEIPT](../evidence_s9/resume_20261020/science_review/DUAL_REVIEW_RECEIPT.json)에 있다. 기존 S6–S8·개발 검증은 재사용했고 고정 source 13/input 3은 유지했다. rtol 1e-8/1e-10 observation 동일 plateau에서 형식적 수렴차수·portable speedup을 주장하지 않았다. 현재 결과 publication은 이 문서의 containing commit이며 최종 배송 receipt/PR 댓글에서 실제 hash를 확인한다. 현재 결과 ZIP의 양쪽 cloud readback은 PENDING이다.

이 디렉터리는 고정 VigilODE를 실제로 호출하는 독립 연구 client다. 기존 REI/BASS owner에 변경을 가하지 않고, 검증된 S8 manufactured closed donor 모델을 Rust로 적분한다. 해의 상태는 `[h,b,y]`이고 h는 Raychaudhuri 방정식으로 독립 진화한다. `Sigma=sqrt(3)|y|/h`다.

## 준비해 실행한 것

- 실제 upstream `mf_into_ls`와 `SmallProblem<4>`를 호출하는 Rust 코드, pinned Cargo.lock, NCP source fetch 및 전체 hash 검증 loader.
- analytic RHS/JVP/Ft, 실제 해의 birth b(u), 고정 birth 시각에서 새 immutable bank/workspace로 restart하는 경로.
- 원래 `balance_p24.rs`의 양의 P24 projection 재사용과, `BigRational`을 통한 정확한 binary64 P2/P4 admission. 원본 owner는 변경하지 않았다.
- 기존 old isotropic/physical anisotropic cohort의 raw 배열과 SHA256을 동일하게 가져오는 입력. 기존 stock을 관측 시각에 재투영하지 않는다.
- 이미 완료한 S8 primal 153개 출력값을 비교 전용으로 추출한 reference. 저장된 reference birth b(u)는 solver input에 없다.
- 각 실패에도 중단 전 raw prefix, 실제 failure 종류, 문제 support 또는 candidate를 남기는 CLI.
- source 게시와 양쪽 cloud readback을 확인한 뒤 실제 실행한 고정 8-case matrix, 독립 Python Fraction/complex-step observer.

## 실행환경

Rust **1.94.1 이상**, Python3가 필요하다. 일반 준비·실행·분석은 Python 표준 라이브러리만 사용한다. `prepare_input.py`는 초기 input 재생성 때만 NumPy/SciPy를 요구한다. 이미 input과 reference가 게시되어 있으므로 NCP에서 이 파일을 다시 실행할 필요가 없다.

기본 실행은 1개 history씩 순차 수행하고 build는 2 jobs다. 추가 worker 최대16, RAM16GiB, 추가 disk4GiB, 개별 job1800초의 기존 상한을 유지한다. 입력/결과를 새 task directory에 놓고 기존 owner worktree와 기존 run 파일을 보존한다. 이 작은 모델에서 MF의 workspace 장점이 속도 우위로 이어진다는 주장은 하지 않는다. 4차원 clock arm은 오차 norm 차원도 달라 고정 accuracy gate로 비교한다.

## 명시적 재현에만 쓰는 과거 NCP 실행 절차

기존 checkout을 덮어쓰지 않는 새 디렉터리에서 게시된 연구 branch를 받는다. root의 closeout에 적힌 **S9 source commit, prereg hash, source 게시·Dropbox·Drive readback**을 확인한다. `evidence_s9/SOURCE_PUBLICATION_GATE.json`은 root가 그 검증을 마친 뒤 남기는 실제 영수증이다.

```bash
task_dir=/scratch/bass_s9_vigilode_20261019
git clone --single-branch --branch research/bass-isotropy-checkpoint-recovery-20261018 \
  https://github.com/cosmosapjw-quantum/bass.git "$task_dir/bass"
cd "$task_dir/bass/research/bass_isotropy_response_20261018"

python3 s9_vigilode/prepare.py \
  --work-dir "$task_dir/runtime" \
  --jobs 2 --build

python3 s9_vigilode/campaign.py \
  --binary "$task_dir/runtime/target/debug/bass-s9-vigilode" \
  --preparation-receipt "$task_dir/runtime/PREPARATION_RETURN.json" \
  --publication-receipt evidence_s9/SOURCE_PUBLICATION_GATE.json \
  --output-dir "$task_dir/results"
```

`prepare.py`는 pinned VigilODE commit의 hash-listed 원본 178개 파일 약5.2MB만 받는다. `cargo`가 registry dependency를 받는 경우에도 lock을 지킨다. 본 실행 전에 source hash가 달라졌거나 binary와 preparation receipt가 다르면 campaign을 시작하지 않는다.

Binary attestation은 실제 성공한 `cargo build --locked --bin bass-s9-vigilode`에 연결된다. `--test`만 실행하면 기존 binary가 있어도 새로 build한 것으로 기록하지 않는다. Python runner만 고친 경우에는 `--reuse-build-receipt /path/to/genuine/PREPARATION_RETURN.json`을 명시하여 기존 성공 build의 source·owner·binary hash가 모두 같은지 검증한 뒤 재사용할 수 있다. 이때 영수증은 `verified_prior_build`, `new_compilation_performed=false`라고 기록한다.

실제 source 자체는 최초 PR71의 게시 SHA와 구별한다.

| 역할 | 고정 식별자 |
|---|---|
| VigilODE 구현 | `a21d573980f66fe02891bd216153443b5352f921` |
| VigilODE source tree | `3eb56734d3dbde83298f6c96e33663b0ad0177b6` |
| VigilODE 최신 결과 게시 | PR71, `ac1cd2a4738c2441c92e5fdae5f70aba35e53544` |
| S8 primary source | `4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613` |
| S8 resume source | `2e6b4a150559b0bea52938896a901f6d438f3582` |
| REI 고정 spectral owner | `0e25846433170d0f420c4cda44a0bedbf02cd177` |

## 명시적 재현 시 기존 source와 offline vendor 재사용

이미 고정 upstream checkout 및 검증된 vendor가 있으면 다운로드 없이 다음 형태로 준비한다. `--vigilode-root`는 전체 selected-file hash를 검사한다. source directory를 수정하지 않는다.

```bash
python3 s9_vigilode/prepare.py \
  --work-dir "$task_dir/runtime" \
  --vigilode-root /path/to/verified/vigilode \
  --vendor /path/to/verified/cargo_vendor \
  --cargo /path/to/cargo --rustc /path/to/rustc \
  --jobs 2 --build
```

전체 upstream Cargo.lock의 registry package 118개를 가진 검증된 vendor를 재사용할 수 있다. 실제 S9 Cargo.lock은 총97개 package(93개 registry, BASS client와 VigilODE 3 crates)이며, `num-rational0.4.2`, `num-bigint0.4.6`, `num-integer0.1.46`를 포함한다. 118개 모두를 이 client에서 컴파일했다는 뜻은 아니다. development AD checker의 `num-dual0.15.1`은 production dependency가 아니다. 독립 callback 검증은 `ad_check/compare_callbacks.py --help`를 참고하고 이미 게시한 raw 결과를 우선 재사용한다.

## 결과를 판독하는 방법

각 case 디렉터리에는 `INPUT.json`, `RAW.json`, `PROCESS.json`, `ASSESSMENT.json`, `console.log`가 생긴다. 전체 `CAMPAIGN_RETURN.json`은 각 case 종료 때 checkpoint된다. `RAW.json`의 `completed`는 적분과 birth admission이 끝났다는 뜻이고, 실제 accuracy/conservation 판정은 `ASSESSMENT.json`의 고정 gate를 함께 읽어야 한다.

`PROCESS.json`을 먼저 보존한 뒤 raw JSON을 읽는다. Timeout 뒤의 잘린 JSON, raw readback 실패, observer 예외 또는 비유한 summary 직렬화 실패는 `raw_readback_or_observer_failure`로 기록하며, 원본 raw/log를 보존하고 다음 등록 case로 진행한다. 이러한 처리 경로와 stale/test-only build 거부는 과학 history를 실행하지 않는 `test_runner_guards.py`의 10개 regression에서 확인했다.

기본 matrix는 K32/n16 P24, 동일 old stock 및 동일153개 출력 시각에서 두 driver와 세 ODE tolerance를 비교한다. 두 fine FLRW controls는 새 synthetic input이며 기존 old stock을 초기화하는 작업이 아니다. birth moment constraint와 angular resolution은 바꾸지 않는다.

feasibility, unresolved geometry, angular precision, exact admission, stock contract, solver failure, timeout을 서로 구별한다. `INNER_P2_PRECISION_LIMIT` 등은 tolerance를 늘려 없애지 않는다. 정확한 candidate가 admission에서 거부되면 `pending_birth`에 남긴다. 수정이 필요하면 같은 실패 결과를 보존한 상태에서 원인에 해당하는 코드만 작게 고치고 새 source/prereg/hash를 게시한 뒤 별도 결과 디렉터리로 실행한다.

## 다음 연구와 남은 의무

다음 연구는 실제 MD14 공급부의 source time·stress·energy bridge를 구성하고 native Einstein/shear feedback에 연결하는 것이다. 새 실행이 필요하면 source·입력·고정 gate와 양쪽 readback을 먼저 완성한다. P6 제약 알고리즘은 미구현이고 full reactive spectral/history 수렴은 미완료다.

S9의 성공 범위는 실제 Rust solver client가 같은 manufactured donor/cohort 모델을 적분하고 기존 보존·birth contract를 지킨다는 데 한정된다. 새로운 native client의 full parameter tangent, 실제 REI/MD14 source owner 피드백, native finite-bin photon/energy 보존, continuum angular accuracy는 별도 의무다. `P2=P4=0`이나 이 작은 closed-history 결과만으로 REI production 또는 full EoR를 승인하지 않는다. Generic upstream continuous-residual authority도 이 `OdeProblem` callback에 자동 부여하지 않는다.

## 후속 실행 인계

현재 Codex/NCP 인계는 [CODEX_HANDOFF_KO.md](../CODEX_HANDOFF_KO.md), 새 ChatGPT 연구 인계는 [NEW_THREAD_HANDOFF_KO.md](../NEW_THREAD_HANDOFF_KO.md)에 있다. 최신 GitHub/백업·source·gate를 직접 읽고 기존 owner 작업 및 실행 중 job을 보존한다. 사용자에게 과거 대화·첨부·ZIP다운로드·사전명령을 요청하지 않는다. 새 캠페인이 필요할 때만 그 단위의 등록된 compile/작은수정/실행 계약을 따른다.
