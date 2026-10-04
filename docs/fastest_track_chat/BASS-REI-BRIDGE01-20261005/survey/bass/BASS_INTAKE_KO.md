# BASS 최신 코드 계보와 REI 소비 경계 조사

조회일: 2026-10-05 KST. 이 문서는 GitHub 연결의 실제 응답과 고정 commit 원문을 읽은 조사 결과이며, 기존 전체 시험을 다시 실행한 결과가 아니다.

## 현재 계보

| 항목 | 실제 원격 identity | 해석 |
|---|---|---|
| 저장소 | `cosmosapjw-quantum/bass` | private, MIT metadata |
| default branch | `main` @ `9c6506e4e2087129a8b674ff10438e5db1a55c9d` | 현재 기능 구현의 채택 기준으로 자동 선택하지 않음 |
| 최신 native 기능 branch | `forward/rust-microphysics-host-20260930` @ `14e0cf0486dc834234122f8bd990fe479f593675` | 이번 추가 구현/게시의 기준 권고 |
| native tree | `9568acee5ce9b4b126f3d50665a71dc720f4db3e` | recursive tree 1,018 entries, truncated=false |
| PR | #132, open, draft=false, main 대상 | merge하지 않고 기존 기능 branch를 계승 |
| 최신 commit 시각 | 2026-09-30T11:07:38Z | Git metadata 기준 |

branch 목록은 세 page, 총 213개를 조회했고, updated 순 최근 PR 30개를 읽었다. 최근 활성 코딩 경로는 PR132다. 이전 BG02, REC source authority, symbolic federation 연구 branch들은 별도 미병합 연구 lane으로 남아 있다. 이미 실행 증거가 있는 예전 geometry/Thomson 연구 전부를 재감사하지 않는다.

native branch와 현재 main의 전체 tree에서 `AGENTS.md`는 없었다. `_rustcore/README.md`는 Rust 1.94.1, locked 의존성, exact REC/REI rev, 자동 Python fallback 금지를 규정한다. 루트 README는 전체 과거 회귀군을 설치 smoke test로 삼지 않고 변경 경로에 해당하는 evidence/CI receipt 명령을 따르도록 한다. 따라서 실제 변경 모듈을 동일 bytes로 포함하는 scoped native harness 검증을 만들 수 있으나 이를 whole-BASS build 통과로 보고해서는 안 된다.

`docs/forward/rust-microphysics-20260930/FORWARD_STATUS.json`의 `current_main_sha=d9e5...`는 과거 시점 기록이다. 이번 조회의 main SHA와 다르다. 역사적 receipt를 수정해서 현재 주장으로 바꾸지 않고 새 intake로 시간과 identity를 구분한다. PR132 본문은 161개 Rust tests 및 fixed-input utilities 검증을 보고하지만 이는 imported historical evidence이며 이번 조사에서 실행한 시험은 0이다.

## 실제 코드 경계

- `microphysics/rei.rs`는 기존 seven kernels의 얇은 dispatcher다. 현재 Cargo REI pin은 `1bda1e8cea7629d31f905e126ba47ec3b3c1d0d8`이고, HHe/FT03 typed state → BASS electron state 연결은 없다.
- `microphysics/visibility.rs::ElectronState::new`는 같은 물질계의 proper H/He 핵밀도[m^-3]와 이온분율에서 `n_e=n_H x_HII+n_He(y_HeII+2y_HeIII)`를 계산한다. 유한성·음수·H와 He simplex를 검증한다.
- `ElectronState::scattering_rate_per_normal_second`는 `q=c sigma_T n_e D`를 계산한다. `D=gamma(1-beta dot e_normal)`는 정확히 한 번 적용된다. direction은 진공에서도 검증한다.
- `integrate_visibility`는 증가하는 normal seconds edge와 고정 cell rate[s^-1]로 역방향 광학깊이를 누적한다. 마지막 edge 이후의 `tau_observer`를 명시하며, cell probability는 `exp(-tau_right)*[-expm1(-q dt)]`다. 마지막 tail 생존확률까지의 제한된 질량을 보존하며 unit mass로 재정규화하지 않는다.
- `compare_opacity`는 같은 ray/clock/boundary에서 절대 rate 차의 L1 tail을 survival/interval mass error bound로 옮긴다. visibility peak 위치·높이 보장은 아니다.
- `microphysics/frame.rs`는 photon occupation source에 D, atomic proper-density local source에 1/gamma를 각각 적용한다. 두 변환은 호환하는 단일 인자가 아니다.
- `kinetic/collision.rs`의 `n_e_sigma_t`는 naked scalar이며 기존 주석/입력은 c와 clock 계약이 명시된 새 visibility rate wrapper가 아니다. 방향별 q를 기존 scalar generator에 그대로 넘겨서 full collision 통합을 주장하면 안 된다.
- `ELECTRON-THOMSON-VALIDITY-CONTRACT.md`는 scalar Q collision의 방향별 generator를 unresolved로 유지한다. local Thomson opacity의 계산과 cold-Thomson/finite-temperature/spectrum validity certificate는 별개의 주장이다.

## 이번 최소 연구/코딩 단위

현재 REI native state를 읽어 HHe/FT03의 proper cm^-3 → BASS proper m^-3 변환을 명시하고, 기존 ElectronState 검증과 normal ray rate 함수를 재사용한다. 그 위에서 caller-supplied clock Jacobian과 fixed cells를 받는 typed schedule을 제공한다. FLRW zero tilt에서 cosmic seconds와 conformal seconds의 `dt=a d eta` 변환, `tau(t)=integral_t^tobs q dt`, probability mass를 직접 유도/검산한다. density dilution, volume average, Q filling factor를 혼동하지 않는다.

API 연결은 실제 pinned REI crate를 이용하고, frame/visibility의 원문 bytes와 새 adapter를 native로 컴파일한다. whole BASS의 diffsol/nalgebra/rayon/private REC 의존성 빌드를 수행하지 않았다면 scoped 모듈 검증으로 표기한다. background evolution, full collision operator, thermal history, observable C_l, existing scientific admission은 이번 단위로 승격하지 않는다.

## REI pin 업데이트의 호환성 범위

기존 REI pin의 `src/group_rates.rs`, `src/lift.rs`, `src/coverage.rs`를 GitHub 고정 commit에서 읽어 로컬 최신 He-RCT source와 대조했다. 세 파일은 SHA256까지 byte-identical이다. seven public functions와 반환형의 기존 본문은 유지되고, `lib.rs` 변화는 새로운 module/export와 설명의 추가다. 정확한 비교 receipt는 `REI_DEPENDENCY_DIFF.json`이다. 최신 source의 원격 commit identity 대조는 root 통합 단계가 수행한다.

핀을 갱신할 때 live contract 네 곳을 함께 맞춘다: `_rustcore/Cargo.toml`, `_rustcore/Cargo.lock`, `_rustcore/src/microphysics/tests.rs`의 `REI` 상수, `scripts/check_microphysics_dependencies.sh`의 `rei_sha`. 과거 `CHILD_DEPENDENCY_LOCK.json`은 역사적 증거로 두고 새 연구 packet에 successor lock/적용범위를 명시한다. REC pin은 이 작업에서 바꿀 이유가 없다.

## 증거 파일

- `REMOTE_STATE.json`: actual branch 및 PR metadata/본문, 선택 기준.
- `TREE.json`: selected native tree 전체.
- `IDENTITY.json`: 선택적으로 읽은 원문들의 Git blob SHA, SHA256, byte size. fetch 반환 UTF-8 bytes를 Git blob SHA와 확인함.
- `sources/`: exact BASS 원문.
- `old_rei/`: 기존 dependency의 직접 비교용 원문.
- `REI_DEPENDENCY_DIFF.json`: 기존 seven-kernel 소유 파일 byte identity.

이 intake의 외부 mutation 및 과학 수치 실행은 모두 0이다.
