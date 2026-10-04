# BASS–REI 다음 연구·코딩 인계

작업 단위는 `BASS-REI-BRIDGE01-20261005`다. 먼저 `LOW_COST_ENTRY.json`을 읽고, 현재 단계의 evidence/review/publication receipt만 추가로 읽는다. 원자 적분이나 과거 전체 시험을 다시 시작하지 않는다. 시험 및 게시의 최종 상태는 root README와 최종 receipt가 소유한다. 이 문서 자체를 실행 성공 증거로 쓰지 않는다.

실행 receipt 기준 scoped Rust20개(bridge10+API1+기존 visibility6+legacy3), 독립 Decimal70 검산786개/actual native140회, 실제 controlled FT03 두 history 검산22029개가 통과했다. history는1000/2000개 interval이며 RCT OFF, H=0이다. 2000-cell의 추가 Thomson depth는2.2336042110622e-4, n_e는102.45→112.83224926834306 m^-3, T는50000→46683.5541528309 K다. 두 discrete history의 opacity L1 차8.00733381490822e-9, survival 최대 차6.5168602e-9는 continuum error certificate나 측정한 convergence order가 아니다. 독립 review와 게시 완료는 각 최종 receipt에서 별도로 읽는다.

## 현재 닫으려는 경계

실제 `rei_microphysics::{HHeModel,Ft03Model,HHeState}`에서 proper electron density를 받아 BASS `ElectronState`로 변환하고 기존 Thomson normal-clock rate 및 finite-interval visibility를 호출한다. BASS 기준은 `14e0cf0486dc834234122f8bd990fe479f593675`, 새로운 REI dependency는 `41e4592aa494b48929dcd23fc8504c169a98a908`이다. 원래 seven REI kernels는 그대로 유지한다.

새 코드 `_rustcore/src/microphysics/rei_visibility.rs`의 입출력은 다음과 같다.

- `electron_state_from_hhe(&HHeModel,&HHeState)`와 `electron_state_from_ft03(&Ft03Model,&HHeState)`는 실제 source validator를 호출하고 proper cm^-3에서 m^-3로 `10^6`을 한 번 적용한다.
- `ReiOpacityCell::{HHe,Ft03}`는 interval마다 model/state, 공통 material frame, normal-ray 방향을 명시한다.
- `integrate_rei_visibility(normal_time_edges_seconds,cells,tau_observer)`는 전자밀도·방향별 rate·기존 visibility 결과를 함께 반환한다. D를 이미 포함한 rate에 추가 D를 곱하지 않는다.

FT03-tagged density adapter는 `gas.electron_density`를 이용한다. FT03 RR/CI/DR RHS를 대신하지 않고, [30000,110000] K rate-domain의 admission을 선언하지 않는다. evolving fixture만 실제 `ft03_adaptive_step`에서 얻은 상태를 사용한다. 둘 모두 진공인 nuclear state는 source validator가 거절하며, 한 원소만 없거나 중성인 정상 state는 허용한다.

현재 API의 clock은 **normal seconds**다. 이론 문서의 conformal 관계 `dt=a d eta`는 유도 결과이며 conformal adapter가 구현됐다는 뜻이 아니다. geometry, a^-3 dilution, Q filling factor, spectral conversion을 API가 추정하지 않는다.

## 바로 다음 단위: BASS-REI-EXP01

REI 소유자가 실제 expanding solution의 cell snapshot을 export하도록 한다. 먼저 작은 non-tilted FLRW history 한 개를 채택한다. 필요한 payload는 증가하는 normal-time edges[s], 각 cell의 proper `n_H,n_He`[cm^-3], `[x_HII,y_HeII,y_HeIII]`, chemistry source commit/model ID, snapshot sampling rule, a(t)/H(t) owner, observer optical-depth tail이다. 새 창작 history를 기존 static FT03 history로 라벨링하지 않는다.

구현할 것은 (1) REI producer의 typed export, (2) BASS의 existing cell adapter 호출, (3) density→rate→tau→probability 결과 반환이다. cell의 density와 chemistry를 같은 accepted stage에서 가져온다. geometry가 제공하는 a^-3를 두 번 적용하거나 Q를 local x로 대체하지 않는다. 

인수 조건은 상수분율의 analytic FLRW density-dilution fixture, 적어도 두 cell 해상도의 관측된 convergence, 같은 history에 대한 direct integral/reference, observer-tail·unscattered-mass 보존, species-resolved electron density 일치다. 실패 시 input/frame/unit/clock 오류와 time-integration 또는 quadrature 오류를 분리한다. uniform continuum enclosure를 제공하지 않았다면 finite convergence만 주장한다. actual expanding export가 없으면 해당 소비만 `BLOCKED_MISSING_EXPANDING_HISTORY`로 종료하고 atomic lane 전체를 재실행하지 않는다.

후속 `BASS-REI-CLOCK01`에서 conformal seconds와 필요하면 conformal length를 **서로 다른 typed clock**으로 추가한다. `eta_s`에는 q_eta=a q_t, `chi=c eta_s`에는 q_chi=a q_t/c다. 같은 physical cells를 다시 표현한 적분 tau와 interval mass가 일치해야 한다. 차원, a>0, monotonicity, overflow, observer-tail 계약을 추가하며 적절한 runtime gate가 열리기 전 naked scalar kinetic API로 연결하지 않는다.

## 독립적으로 남겨 둘 단위

| 작업 | owner | 다음 입력 및 완료 조건 |
|---|---|---|
| `BASS-THOMSON-DOM01` | BASS photon/electron authority | 같은 event/ray/segment의 calibrated photon energy support와 electron temperature; cold-Thomson 또는 finite-T/KN error budget을 별도 승인 |
| `BASS-KINETIC-GEN01` | BASS transport | 방향별 generator 유도 및 collision gain/loss 시험. `M_D(K-I)`를 scalar-q 단축으로 대체하지 않음 |
| `RCT-STEP01` | rei_bianchi | 실제 FT03 implicit residual, accepted half stages, 누적 RCT event/thermal/escape ledger. RCT 기본 OFF 유지 |
| `HE-F2` / mixed native | BASS_HE | 새 RCT consumer return에 대한 owner acceptance와 종별 reference gate; 현재 physical admission=false 유지 |
| `CR-F04C` | bass_cr | 실제 FT03 residual 및 해당 owner box. F04B frozen source/full discarded candidate 인증을 accepted two-half나 continuum으로 확장 금지 |
| `HH-F2` / F07 | WU088_HH/REI | 실제 rate domain, cutoff, event/heat owner, 관측량 budget 수신. 현재 atomic-off baseline을 막지 않음 |

기존 original atomic 계산 계획은 별도 장기 lane으로 남아 있다. 공급자 표/fit과 새 고정 인스턴스가 필요할 때 해당 lane의 가장 최근 machine-readable handoff를 호출한다. 네 repo를 자동 merge하거나 기존 failed scientific gate를 초기화하지 않는다.

## 코드 실행·게시 계약

새 source-only harness는 정확한 BASS frame/visibility/rei/새 adapter와 전체 pinned REI dependency를 컴파일한다. 이 검증을 whole-BASS crate 또는 Python/native ABI 시험으로 바꾸어 보고하지 않는다. 변화가 없는 heavy dependency·full historical suite는 새 필수 gate로 추가하지 않는다. 명시적으로 whole-BASS native release를 시작할 때만 현재 lock/cache/빌드 환경을 읽고 해당 build gate를 수행한다.

```bash
export PATH=/tmp/rec_rust_1941/bin:$PATH
cargo test --manifest-path coding/scoped_harness/Cargo.toml --locked --offline
```

위 명령은 이 packet root 기준이며 `/tmp/rec_rust_1941`은 이번 실행 환경의 compiler 위치다. 다른 host에서는 `rustc --version`으로 Rust1.94.1의 실제 위치를 확인하고 PATH만 조정한다. scientific tolerance나 dependency revision을 환경 복구 이유로 변경하지 않는다.

BASS 게시 대상은 기존 `forward/rust-microphysics-host-20260930`/PR132, REI 반환은 현재 `forward/rust-reion-kernels-20260922`의 additive consumer-return이다. publish 직전 actual tip을 조회하고 non-force ancestry로 현재 다른 스레드 변경을 보존한다. main merge, 새 PR로 전체 개발을 분기하는 일, automatic RCT enablement는 이 인계에 포함하지 않는다. 실제 commit/object identity와 Drive+Dropbox ack는 최종 게시/백업 receipt에 기록한다.
