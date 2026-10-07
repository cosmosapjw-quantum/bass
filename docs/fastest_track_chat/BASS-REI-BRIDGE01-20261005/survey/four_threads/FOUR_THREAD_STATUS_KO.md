# 네 연구 스레드의 bass 결합 입력 상태

2026-10-05 KST의 GitHub 실제 branch/ref와 정본 파일을 읽은 범위다. `REFS.json`에 관측시각과 commit/tree, `SOURCE_IDENTITY.json`에 읽은 23개 파일의 commit/blob/byte 길이/SHA-256을 기록했다. 네 저장소에 mutation하거나 과거 과학 시험을 재실행하지 않았다. 아래 시험 수는 각 생산자가 게시한 실행 증거를 수신한 값이며 이번 bass 루프의 신규 시험 수가 아니다.

| 스레드 | 현재 읽은 branch | commit | 이번에 활용할 결과 | 유지할 상한 |
|---|---|---|---|---|
| rei_bianchi | forward/rust-reion-kernels-20260922 | 7a15daa38b60a5174315747b9194564dc2d4eb8b | 실제 HHe/FT03 state와 전자 밀도, RCT 국소 RHS | 실제 expanding consumer, RCT stepper, F04 uniform certificate 미완료 |
| BASS_HE | research/shared-c64-crossrepo-20260928 | faea0580e5751ffaf23012f91649c34e48fbb7cb | HE-FLRW02B 종별 흡수 reference, 새 RCT consumer return | mixed-native gate 및 HE-F2 owner acceptance 미수신, physical admission=false |
| bass_cr | research/r4q-gap-closure-20261001 | da8b174267e27f0a70ee7ff12fb130179c1abfab | F04B frozen-source Schur 잔차·native bit binding | 새 FT03/accepted two-half/continuous ODE/우주론 history로 인증 이월 불가 |
| WU088_HH | research/r31ao-unequal-order-ladder-20260930 | 1c1b0971a19a6449bba09d8b8b1febc1ea6162dd | F1D cutoff 횡단·민감도 및 사건/열 회계 조건 | F07 domain/cutoff 소비자 결정 대기, HH-F2 미결합 |

REI와 HE는 직전 루프의 최종 전달 commit과 동일하다. CR/HH는 관련 이름의 최신 연구 branch를 실제 branch 목록에서 찾았고 최근 handoff가 있는 tree를 읽었다. 저장소 `main`을 최신 fastest-track 작업 branch로 간주하지 않았다.

## REI: 실제 소비 가능한 상태와 코드

`rust/rei_microphysics/src/hhe_events.rs`의 `HHeModel::electron_density(&HHeState)`가

\[
n_e=n_Hx_{\rm HII}+n_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII})
\]

를 **proper cm⁻³** 단위로 제공한다. `HHeState.fractions` 순서는 HII, HeII, HeIII이고, H/He 각각의 핵수로 정규화한다. `n_e/n_H`와 전체 핵수 정규화 electron fraction을 혼용하면 안 된다. density 입력은 proper이고 static controlled fixture의 H=0을 임의의 팽창 history로 바꾸어 읽지 않는다.

FT03는 온도의존 RR/CI/DR 및 Verner PI를 쓰는 실제 별도 successor다. seven-state native integrator가 있지만 현재 model은 H=0 controlled Case-A이고 온도 guard는 [30000,110000] K다. `FT03.gas`의 alpha/beta=0을 기존 HHe RHS에 그대로 넣으면 FT03 RR/CI/DR가 누락된다. source/electron state bridge가 chemistry RHS를 복제·대체할 이유는 없다.

He RCT 루프는 국소 `combined_hhe_rhs` 및 `combined_ft03_rhs`를 구현했다. 실제 통합 116시험, 독립 Decimal 검사 12789개, FT03 추가 검사 212개의 최종 receipt를 수신했다. 기본값 OFF, 명시적 KF96/GM25 선택, 평균 광자에너지 caller input에 조건부인 열 closure다. RCT 반응 HeIII+HI→HeII+HII+γ의 **직접 free-electron source는 0**, 현재 primary photons는 tracked groups 밖으로 모두 escape한다. 따라서 RCT event rate를 Thomson scattering rate나 전자 source로 직접 더하지 않는다. RCT implicit stepper 연결은 다음 `RCT-STEP01`이다.

FLRW03는 stage별 R/nH 사건 누적, birth-time spectrum 및 threshold/energy 소유권의 reference·계약을 닫았지만 native expanding consumer는 열려 있다. REI-F04는 실제 FT03 구현까지만 partial이다. 서로 다른 source/geometry/stage의 증거를 합쳐 전체 history 완료로 간주하지 않는다.

## HE: consumer return과 owner acceptance의 구분

`CURRENT_FASTEST_STATE.json`에는 과거 `RCT_INSTANCE_NOT_RECEIVED`가 남아 있다. 현재 tree에는 더 새 `consumer_returns/REI-HE-RCT01_20261005/HE_F2_RCT_CONSUMER_RETURN.json`이 실제 존재하며 native commit 41e4592aa494b48929dcd23fc8504c169a98a908과 local conditional RHS 결과를 구체적으로 반환했다. 이 불일치는 old snapshot과 additive return의 시간 차이다. **새 return 게시됨**으로 상태를 읽되, 공급자 owner의 수락 판정까지 완료됐다고 바꾸지 않는다.

HE-FLRW02B는 fitted-source 종별 reference와 식별가능성 분석을 완료했다. 5 reference states, 9 σ points, 6 active channels의 total-photon/energy projection에는 rank3/nullity3가 있어 전체량 보존만으로 종별 흡수를 검증할 수 없다. 종별 anchor를 추가해야 rank6이 된다. 이는 bass의 photon/electron source ledger에서도 전체 광자·에너지 수지뿐 아니라 종별 source를 보존할 이유가 된다.

해당 mixed native gate는 `OWNER_NATIVE_RESULT_PENDING`; 새 Python 11개 시험과 기존 84 native suite receipt를 mixed gate 완료로 합산하지 않는다. 비교 허용오차 5e-14 relative+1e-300 absolute는 이 source reference에만 고정된 기준이며 새 bass test 기준으로 무단 이월·완화하지 않는다.

## CR: 정확한 인증의 적용 범위

F04B 연구 문서는 실제 native 저장 bit의 photon residual을 reduced fraction residual로 전달하는 Schur 보정, thermal/escape 항등식, 성분별 resolvent posterior 및 같은 dt-family의 민감도를 유도했다. 새 focused tests42가 보고되어 있다. 별도 native producer는 정확히 한 번의 full/discarded BE candidate 실행 및 10개 binding 시험을 보고한다. 둘을 이번 루프의 새 52개 실행으로 합산하지 않는다.

고정 synthetic F03 model의 dt=1e8 s candidate에서 root-distance infinity upper는 약1.4758856593968439e-18이다. 이것은 exact-real BE root와 저장 native fraction의 차이이며 연속 ODE 오차가 아니다. 온도의존 FT03, expanding geometry, accepted half1→half2 조합 또는 새 초기 box에는 적용하지 않는다. 다음 CR-F04C의 실제 FT03 residual/owner box intake는 별도다.

CR_OFF_FASTEST 유지, CR-F0 실제 dispatch에서 source/provider/callback load가 0임을 관측한 증거는 아직 null이다. G02 UNRESOLVED, production HOLD, capture=false, all_bound OPEN, b_grid NO_GO를 보존한다. 이 지원 연구가 bass scalar Thomson bridge의 새 필수 대기 조건이 되는 것은 아니다.

## HH: cutoff sensitivity를 현재 실행 조건으로 오독하지 않기

HH-F1D는 연속 해의 유일성과 BE 다중 root를 구분하고 raw floor의 유한 열적 수명, expanding guard의 명시적 시간항, 횡단 saltation, 사건/열 장부와 조건부 event-time error를 유도했다. proof script 1회, symbolic identities27, exact assertions49가 보고돼 있다. 실제 HH fit/root solver/stepper/consumer/history/primitive/NCP 실행은 모두 0이다.

raw 3000 K floor는 물리적으로 승인된 low-T rate가 아니다. 단열팽창 normal-speed 분석을 실제 photoheating·recombination source와 혼합된 시스템의 transversality 인증으로 바꾸지 않는다. 실제 F07 domain/distribution/constants·event/heat/binding owner·관측량 budget과 cutoff 정책이 도착하기 전 HH-F1은 WAITING_ON_REI_DOMAIN, HH-F2는 NOT_INTEGRATED다. HH-off baseline은 이 결과를 기다리지 않는다. legacy accepted24/289, missing265 및 B22 OPEN은 그대로다.

## bass 루프에 필요한 결정

1. **즉시 사용 가능:** 실제 REI state의 charge-derived proper electron density와 단위/시간/좌표 계약. bass의 Thomson 계수/opacity 연결은 원자 정밀 lane 재실행 없이 이 경계로 시작할 수 있다.
2. **구현 시 명시할 것:** bass가 SI를 쓰면 cm⁻³→m⁻³는 10⁶을 한 번 적용한다. proper-time scattering rate와 conformal-time rate의 a 인자, signed optical-depth convention은 별도로 고정한다. backward visibility와 forward accumulated optical depth를 같은 부호로 추정하지 않는다.
3. **광자 ledger 경계:** Thomson 산란과 ionizing absorption은 별개 채널이다. chemistry photon3 density를 자동으로 CMB polarization hierarchy 상태로 해석하지 않는다. RCT escaped energy를 가상의 tracked CMB source로 주입하지 않는다.
4. **회귀 조건:** H-only/HeII/HeIII 및 완전중성 경계, density scaling, rate 단위, 비영 shear와 tilt를 0으로 보내는 계약, electron source에 RCT를 직접 더하는 부정대조가 적합하다. 구체적인 구현·시험은 bass source 담당 루프가 현재 API를 읽은 뒤 정한다.
5. **대기 조건을 좁게 유지:** scalar state/rate bridge의 검증과 실제 Bianchi polarized transport·배경 solver·expanding reionization history는 서로 다른 완료 단위다. HE/CR/HH 미완료를 숨기지 않으면서 atomic-off baseline 개발을 진행한다.

이번 문서는 입력 survey이며 독립적인 physical source accuracy, 전체 archive restore, uniform certificate, scientific/production promotion 또는 네 스레드의 자동 종결을 주장하지 않는다.
