# 다음 연구 루프: He RCT를 실제 적분기에 연결

실제 실행 결과는 `evidence/FINAL_INTEGRATION.json`과 `evidence/INDEPENDENT_RESULT.json`에 고정돼 있다. Full Rust 시험116개(기존84+수신 FT03 8+RCT24), independent decimal70 E2 검사12789개와 FT03 E2X212개가 PASS다. Native 호출422회 중96 states×4 modes=384 event calls를 포함한다. E2X는12 native calls(9closed+3GM25거절), 최대 gross-scaled error4.181e-16이다. 이 결과는 원래 HHe 및 actual typed FT03 local rate/event/conditional RHS 검증이며 두 RCT time stepper는 미연결이다. 독립 최종 검토는 confirmed, open blockers0이며 기존 `review/FINAL_REVIEW.json`과 추가 `review/POST_FT03_REVIEW.json`에 고정돼 있다.

현재 묶음의 목표는 HeIII+HI → HeII+HII+γ에 대해 원자율 선택, 실제 Rust provider, 사건수 RHS, 조건부 energy closure를 코딩 가능한 계약으로 닫는 것이다. `coding/NATIVE_IMPLEMENTATION_STATUS.json`, `evidence/FINAL_INTEGRATION.json`, `review/FINAL_REVIEW.json`의 **실제 파일 존재·판정·소스 identity**를 읽고 현재 구현 완료 범위를 결정한다. 이 handoff의 텍스트 자체는 시험 PASS 증거가 아니다. receipt 경로가 달라졌다면 현재 README가 지시한 실제 receipt를 읽고 경로를 정정한다.

먼저 `LOW_COST_ENTRY.json`, `PROVIDER_SELECTION_RECORDS.json`, `theory/CONTRACT.json`, native status와 독립 검증 결과만 읽는다. 원자 논문·전체 repo·과거 suite를 처음부터 다시 조사하지 않는다. 현재 loop의 baseline pin은 REI `ccbc15019296b9128a90fa45b9c68c7daddc7b77`, supplier는 HE `21d5b8075429903d195d6e0e0c24a10c00b21063`이다. 실제 게시한 native code commit은 `41e4592aa494b48929dcd23fc8504c169a98a908`이며 현재 실행은 이 revision을 기준으로 한다.

## 이 루프에서 선택한 범위

기본값은 `RctSelection::Disabled`다. bounded opt-in profile은 KF96 nominal prescription을 기본 비교 경로로 두고 GM25를 공통 온도 범위의 대안으로 제공한다. 이는 KF96의 더 넓은 nominal numerical call window를 이용하기 위한 선택이며 물리 정확도의 우월성 판단이 아니다. 두 값을 더하거나 온도에 따라 자동 전환하지 않는다. 공통 sensitivity는 1000–10000 K 안에서만 한다. KF96 단독 창은 1000–10000000 K, GM25는 200–10000 K이며 범위 밖 입력은 명시적으로 거절한다. 과거 FT03 guard는 현재 synthetic baseline에 이월하지 않는다.

`PROVIDER_SELECTION_RECORDS.json`은 HE exporter 0.1.1의 **실제 thermal_rate 요청**으로 생성한 두 scalar record를 담는다. event-count packet을 열율로 이름만 바꾸지 않았다. common provider schema의 모든 필수 필드를 채웠으며 density product는 소비기가 한 번만 적용한다. `consumer_admission=false`와 source photon/heat/recoil/spectrum null은 물리 공급기·에너지 moment의 미승인을 유지한다. 이는 현재 명시적 opt-in 연구 RHS의 구현 가능성과 별개다.

`RctProvider::events`는 열 closure 없는 사건수·분율·chemical ledger다. 열 RHS와 합치려면 `EscapingMeanPhotonEnergy::research_input_ev(Ebar)`를 명시하고 `RctSelection::Escaping`을 사용한다. Ebar는 finite positive caller input이며 source spectrum의 예측값이 아니다. run manifest가 정확한 Ebar, 원천/시나리오 목적, API provenance class를 기록한다. 현재 시험의 Q−1,Q,Q+1은 synthetic validation scenario다. Q를 기본 물리 광자에너지로 숨겨 넣지 않는다.

에너지 소유권은 chemical −QR, thermal (Q−Ebar)R, escaped radiation Ebar R이다. 모든 primary RCT photon은 현재 tracked radiation 밖으로 나간다. 이 제한 모형은 지연 재흡수·OTS·spectral grouping·bulk/recoil/momentum tensor를 제공하지 않는다. 음의 thermal 항도 가능하므로 RHS 에너지 항등식이 positivity/time-step admission을 보장하지 않는다.

## 다음 단일 PR의 구체적인 일

다음 bounded node는 `RCT-STEP01`: actual Ft03 successor time integrator를 우선 target으로 고정하여 opt-in RCT를 연결한다. `combined_hhe_rhs`와 `combined_ft03_rhs`는 모두 구현·검증됐지만 기존 implicit_hhe_step/ft03_implicit_step는 각 baseline update/residual을 직접 사용하므로 RCT가 자동 적용되지 않는다.

1. 실제 source selector, closure input, 온도 domain을 가진 step contract를 고정한다. accepted state와 모든 stage에서 같은 source를 사용하고 범위를 벗어나면 재시도/실패를 기록한다. clamp·fallback source switch는 넣지 않는다.
2. RCT integrated event count를 기존 RR event와 별도 보존한다. accepted two-half-step 사건수는 두 half-step의 합이며 최종 endpoint rate×전체 dt로 대체하지 않는다. Escaped photon count도 energy reservoir와 분리한다.
3. 같은 endpoint/state에서 species, thermal, escape, photon balance와 residual을 계산한다. 새 RHS만 잔차에 넣고 기존 positive block update가 다른 방정식을 푸는 불일치를 허용하지 않는다. energy ledger와 event stage의 time quadrature를 맞춘다.
4. 먼저 정적 isolated RCT의 analytic solution으로 extent ξ(t)를 비교한다. 초기 HI density A, HeIII density B에 대해 dξ/dt=k(A−ξ)(B−ξ); A=B 극한과 둘 중 하나가 0인 경계를 포함한다. 이어 제한된 coupled H/He fixture만 적분한다.
5. OFF baseline equality, electron/nuclei conservation, event number와 escaped number 일치, total energy, positivity, source-domain rejection, 실패 후 accepted state 불변을 검증한다. 같은 모형의 independent reference를 사용한다.

이 PR의 성공조건은 실제 native integrator의 제한된 RCT extension이다. F04 interval/Jacobian certificate나 실제 재이온화 history가 아니다. 새 수치 오차 기준은 실행 전에 기록하고 기존 strict local error/width gate를 변경하지 않는다. 필요하면 후속 `RCT-STEP02`에서 matching Jacobian, nonlinear solver, event-consistent error estimator를 다루되 한 번의 완결 범위를 유지한다.

## 이후 물리 연구의 분기

`RCT-SPEC01`은 source spectrum/energy-weighted rate 또는 정당화 가능한 conditional moment를 확보하는 별도 연구다. Scalar k만으로 Ebar나 angular/recoil moment를 유도하지 않는다. 그 뒤 `RCT-TRANS01`에서 그룹별 number와 energy를 동시에 보존하는 projection 또는 별도 emission channel을 결정한다. 종별 absorption/OTS 확률과 secondary는 별도 소유권을 가져야 한다.

`RCT-SOURCE01`은 KF96/GM25 source discrepancy가 실제 관측량에 중요한 경우에만 좁은 반응 채널의 source 정밀도 연구를 재개한다. 단순히17배라는 이유만으로 기존 atomic full suite를 다시 돌리지 않는다. 현재 sensitivity 두 source는 rigorously bounded error band가 아니다.

HE-F2에 반환할 것은 실제 module/commit/path identity, 두 provider record, 선택된 source/온도/closure/run record, affected test receipts다. HE-F2는 이를 수락·거절하는 작은 changed-contract intake를 수행한다. 현재 가장 최신 HE state를 이 스레드가 대리로 COMPLETE로 바꾸지 않는다. REI-F09와 HE-F3/HH-F3의 응용 종결은 같은 실제 paired cosmological campaign receipt가 생겼을 때만 한다. REI-F08 baseline은 이 optional RCT extension을 기다리지 않는다.

원래 원자 lane은 [HE LEGACY_LANE.json](https://github.com/cosmosapjw-quantum/BASS_HE/blob/21d5b8075429903d195d6e0e0c24a10c00b21063/docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/LEGACY_LANE.json)에 고정해 두었다. HE-L1/L2/L3는 PARKED_OPEN이며 구체적인 spectrum/source/state/kinetic dependency가 생긴 항목만 다시 호출한다. Bianchi 방향성·finite tilt·재결합 coupling은 기존 큰 연구 DAG에 남는다.

실행 반환에는 입력/출력 SHA-256, native source commit, 실제 명령·종료코드·시험 수·오차 지표, 최초 실패와 수정, 성공한 claim 및 미수행 claim을 기록한다. GitHub와 Drive/Dropbox backup은 provider acknowledgment 및 identity/size를 확인한 수준만 보고하며 전체 restore를 하지 않았다면 RESTORE_VERIFIED라고 쓰지 않는다.

## 게시 직전 동시 업데이트 수신

REI `6279036f06c9ba4d47574beab90b48fc2c6f9ba7`은 별도 `Ft03Model`/`ft03_rhs`/`ft03_implicit_step`/`ft03_adaptive_step`와 온도 의존 HG RR·CI 및 DR thermal model을 실제 추가했다. HE 최신 `e4d2753ea45593ade6c3fd3a7fea81f92cfd1a15`은 mixed-HHe absorption reference와 이 변경의 late ACK를 추가했으며 RCT provider 변경은 없다. 자세한 근거·동일성은 `survey/FINAL_DELTA_KO.md`와 `FINAL_DELTA_IDENTITY.json`에 있다.

과거 FT03 guard를 원래 synthetic HHe baseline에 적용하지 않는다는 기존 판단은 유지한다. 그러나 **새 실제 Ft03Model에는 [30000,110000] K guard가 현재 유효하다**. 추가 RCT 검증은 원래 HHeModel wrapper와 새 typed combined_ft03_rhs까지 포함한다. 새 Ft03 stepper와는 아직 연결하지 않았다. GM25 창은 새 Ft03 guard와 겹치지 않는다. KF96 창이 덮는 것은 source call domain 충족일 뿐 물리 또는 energy closure 승인이 아니다.

`RCT-STEP01`의 첫 행동은 actual Ft03 successor time integrator를 우선 target으로 고정하는 것이다. 원래 controlled HHe stepper는 별도 모형으로 유지한다. Ft03을 선택하면 현재 HG temperature-dependent rates, RR kinetic/DR moments, thermal residual과 accepted source-stage bookkeeping을 보존한다. **Ft03Model.gas의 alpha/beta 배열은0이므로 combined_hhe_rhs(&ft03.gas)는 실제 Ft03의 RR/CI/DR를 누락한다.** 추가 구현한 combined_ft03_rhs는 RctProvider.closed_events(&ft03.gas,...)의 사건기여를 actual ft03_rhs에 더한다. 이 local composition은 검증 완료됐으며 다음 stepper/residual도 같은 물리를 사용해야 한다. Time integration 연결 완료는 주장하지 않는다.

F04는 새 actual successor 구현까지 진행했지만 반환 상태는 partial이며 full_F04_completed=false다. 균일 interval/root/J/H/remainder certificate와 기존 gate는 그대로 남는다. FLRW03 chat reference의 integrated event/nH 및 birth/edge/work 계약도 새 문서로 보존하며, 이번 RCT local RHS 통과를 그 native integration gate의 완료로 전용하지 않는다.

표현가능성 범위: FT03의 nonzero-factor product-underflow 거절 계약을 RCT finite-point 검증이 전부 계승했다고 주장하지 않는다. RCT local wrapper의 finite-value 검사는 그 별도 representability 인증이 아니며 실제 stepper 결속 때 affected numerical contract로 처리한다. HE-F2로 전달할 구체적인 owner-return은 `publication/he_consumer_return/HE_F2_RCT_CONSUMER_RETURN.json`과 동명 KO 문서에 준비돼 있다.
