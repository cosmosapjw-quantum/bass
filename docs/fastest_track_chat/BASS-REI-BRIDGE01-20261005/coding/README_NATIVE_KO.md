# BASS의 typed REI → Thomson 경계

실제 BASS 소스에 `microphysics::rei_visibility`를 추가했다. 입력은 실제 REI의
`HHeModel + HHeState` 또는 `Ft03Model + HHeState`이며, 출력은 기존 BASS의
`ElectronState`와 고정된 normal-time 셀의 visibility다. 새로운 화학식이나
Thomson 적분기를 복제하지 않았다.

REI revision은 `41e4592aa494b48929dcd23fc8504c169a98a908`으로 고정했다.
REC revision `d3cc6e0120061f113d28e7a3a55a2e3dd561e81e`은 그대로다.
`Cargo.toml`, `Cargo.lock`, 기존 pin 검사와 dependency checker는 REI SHA만
바뀌었다. `BASELINE_PRESERVATION.json`은 실제 변경 경로 8개와 파일별 해시를
기록하며, 나머지 입수한 BASS 파일의 원문을 보존했음을 확인한다.

## 구현 계약

- `electron_state_from_hhe`는 먼저 원 source의 `electron_density`를 호출한다.
  따라서 fraction뿐 아니라 전체 source model/state의 유효성도 확인된다.
  원 proper nuclear density의 cm^-3를 `1e6` 배로 m^-3로 바꾸고, 기존
  `ElectronState::new`가 전자 수를 구성한다. 변환 overflow는 명시적 오류다.
- `electron_state_from_ft03`는 `model.gas`의 같은 경계를 사용한다. 이는
  **density-only snapshot** 계약이다. FT03 rate-fit T 영역의 유효성은
  보증하지 않으며, opacity를 위해 FT03 thermal RHS를 불필요하게 평가하지 않는다.
- `ReiOpacityCell`은 각 셀의 실제 모델·상태·material frame·unit ray direction을
  보유한다. 기존 `ElectronState::scattering_rate_per_normal_second`가
  `D = gamma (1 - beta dot e)`를 한 번 적용한다. 기존 `integrate_visibility`가
  고정 time edges 및 observer optical-depth tail을 그대로 적분한다.
- SI Thomson 상수는 BASS 소유다. Source의 임의 상수와의 호환성까지 이 density
  adapter가 인증하지 않는다. 제공된 controlled history에서는 실제 source
  `c_cm_s == 100 * C_M_S`를 명시적으로 검사한다.
- 중성 상태 및 한 종류 nuclei 부재는 허용한다. 양쪽 nuclear density가 모두 0인
  모델은 source validation이 거절한다. 전자 수가 0이어도 ray direction을 검증한다.

이것은 기존 cold-Thomson 근사 아래의 수치 연결 도구다. 유한 온도의 상태로부터
전자 momentum tail·cold limit·polarized collision kernel의 물리적 유효성이
새롭게 확보되지는 않는다. 물리 admission은 false다. RCT는 OFF이고, legacy
kinetic collision 경로 및 geometry/RT solver에는 연결하지 않았다.

## 실제 실행과 범위

`scoped_harness`는 실제 전달하는 BASS `frame.rs`, `visibility.rs`, `rei.rs`,
`rei_visibility.rs`와 source-byte-identical REI crate를 직접 컴파일한다.
새 모듈이 없는 상태에서 E0432 RED를 먼저 보존했고, 구현 후 **20개 검사**가
통과했다: 새 bridge 10개, 존재 회귀 1개, 기존 visibility 6개, 원래 REI dispatch
시험 2개 및 pin identity 시험 1개. 원 dispatch 두 함수는 기존 API 일곱 개를
모두 호출한다. REC 및 나머지 BASS 의존성이 포함된 full BASS build 결과를
뜻하지 않는다. `rustfmt` 실행 파일은 현 환경에 없어 formatter는 실행되지 않았다.

```bash
cargo test --offline --manifest-path coding/scoped_harness/Cargo.toml
cargo build --offline --manifest-path coding/scoped_harness/Cargo.toml --bin rei_visibility_probe
```

Rust 1.94.1로 실행했다. 독립 snapshot 및 history 입력 형식은
`PROBE_CONTRACT.json`에 고정했다. 실제 main-path probe는
`bass/_rustcore/examples/rei_visibility_probe.rs`다. scoped harness의 binary도
그 원문을 직접 사용한다.

```bash
echo 'history 1000 0.2' | coding/scoped_harness/target/debug/rei_visibility_probe > history.json
```

history command는 실제 `Ft03Model::controlled()`의 initial state부터 실제
`ft03_adaptive_step`으로 총 `1e14 s`를 진행한다. Caller가 정한 같은 간격의
edges를 유지하며, 각 visibility 셀은 left-endpoint state를 쓴다. 실패한 step을
임의의 history로 대체하거나 retry로 grid를 바꾸지 않는다. 이 probe의 frame은
rest이므로 source material clock과 normal clock이 일치한다. 온도·fractions·
전자 수를 각 edge에서 출력하며, source residual와 local error도 기록한다.
시간에 따라 변하는 FT03 RHS를 실행한 수치 연결 실험이며, FLRW cosmological
history나 관측 visibility의 예측은 아니다.

Root의 독립 Decimal 검산과 n=1000/2000 실제 history 결과는 이 폴더 바깥의
최종 evidence에서 관리한다. 여기 native 결과를 그 검증의 대용으로 삼지 않는다.
