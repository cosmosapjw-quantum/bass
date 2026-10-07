# He RCT 선택·provider·closure: REI-HE-RCT01

2026-10-05 KST. **명시적 원자율 선택, 사건 회계, 조건부 열·탈출 광자 closure를 실제 REI native RHS에 연결했다.** 구현·유한 수치 대조·독립 검토는 완료했다. 원자율의 물리 정확도, 방출 spectrum, 기존 implicit stepper와의 연결, 관측량 history는 승인하지 않았다.

## 선택과 원전

초기 BASS_HE 21d5b807와 REI ccbc1501을 읽은 뒤, 동시 업데이트를 최종 BASS_HE e4d2753ea45593ade6c3fd3a7fea81f92cfd1a15와 REI 6279036f06c9ba4d47574beab90b48fc2c6f9ba7까지 대조했다. HE의 추가 변경은 공급기 변경 없는 HE-FLRW02B 문서다. REI의 실제 온도 의존 FT03 추가를 보존하고 전용 연결 함수를 추가했다. REI baseline의 RCT 제외는 유지하며 별도 opt-in 연구 인스턴스를 만들었다. 기존 원자 산란 계산을 다시 수행하지 않았다.

| 선택지 | 계수 [cm³/s] | 엄격한 수치 호출 구간 | 이번 역할 |
|---|---:|---:|---|
| KF96 nominal | 1.00e−14 | 1000–10⁷ K | 명시적으로 선택하는 기본 연구 profile |
| GM25 constant | 1.70e−13 | 200–10000 K | 별도 대안; 두 source 비교는 1000–10000 K |

KF96의 넓은 호출 구간은 코드 profile 선택 이유이며 물리적 우월성의 근거가 아니다. 전역 default는 OFF이고 자동 선택·온도 clamp·외삽·두 계수 합산을 금지한다. 기존 HHe synthetic baseline에는 해당하지 않는 30000–110000 K guard가 새 Ft03Model에는 실제 적용된다. KF96 범위는 이를 포함하지만 GM25는 포함하지 않으므로 hot FT03 호출에서 거절한다. 이는 정확도 판정이 아니다.

KF96 Eq.7/Table1의 He²⁺ nominal prescription과 공개 저자 Fortran의 해당 행을 교차 확인했다. 문헌의 낮은 경계는 대략적인 값이고, 정확한 1000 K 경계는 기존 공급기의 수치 정책이다. 저자 Fortran의 범위 밖 clamp를 그대로 계승한 구현은 아니다. GM25 Appendix B.3는 200–10000 K에서 1.70e−13 cm³/s 근사와 KF96보다 큰 값을 보고한다. **17배 차이는 미해결 출처 차이이며 신뢰구간이나 오차 한계가 아니다.** 원 단면적 재적분도 하지 않았다.

원전과 exact supplier 코드·packet 식별은 sources/SOURCE_LEDGER.json에 있다. 참고 원전은 [KF96](https://doi.org/10.1086/192335), [GM25 v1 Appendix B.3](https://arxiv.org/html/2511.21966v1), [W82](https://doi.org/10.1103/PhysRevA.26.3164)이다. 수치 사실과 기존 공급기 코드를 재사용했으며 원 논문 PDF를 재배포하지 않는다. 공개 열람 가능성과 무조건 재배포 권리는 구분했다.

## 사건·열·광자 계약

선택한 채널은

\[
\mathrm{He^{++}+H(1s)\longrightarrow He^+(1s)+H^++\gamma}.
\]

기체 정지계, 공통 온도의 Maxwell 분포, 상대 bulk drift 0, 명시된 W82 ground-state isotope scenario를 가정한다. KF96 자체의 isotope 지원이 해결되었다고 주장하지 않는다. proper density를 cm⁻³, 시간은 s로 쓰며 natural units를 사용하지 않는다.

\[
R=k(T)n_{\rm HI}n_{\rm HeIII},\qquad
\nu=(-1,+1,0,+1,-1,0)
\]

에서 species 순서는 HI,HII,HeI,HeII,HeIII,e다. H와 He 핵수, 전하, 자유전자 수가 보존된다. 분율 RHS는

\[
\dot x_{\rm HII}=R/n_H,\quad
\dot x_{\rm HeII}=R/n_{\rm He},\quad
\dot x_{\rm HeIII}=-R/n_{\rm He}.
\]

해당 핵 밀도가 0이면 새 adapter의 그 분율 기여를 0으로 정의해 0/0을 피한다. 실제 source 온도 검사는 반응물이 없을 때도 수행한다. FLRW에서 핵수 보존으로 나누면 분율에 별도 −3Hx 항을 넣지 않는다. 이번 루프는 우주론 시간 적분을 실행하지 않았다.

기존 모델의 binding-energy 상수를 쓰면

\[
Q=\chi_{\rm HeII}-\chi_{\rm HI}=40.819325400298\ {\rm eV}
\]

이고 chemical energy 변화는 \(-\epsilon_{\rm eV}QR\)이다. 여기서 \(\epsilon_{\rm eV}=1.602176634\times10^{-12}\ {\rm erg/eV}\). 양의 finite Q를 검사한다.

Scalar k(T)는 열·광자 에너지 moment를 제공하지 않는다. CountOnly는 사건·species·primary photon birth만 반환하며 미정 에너지를 0으로 대체하지 않는다. 실제 thermal RHS와 조합하는 경로는 아래의 별도 입력을 반드시 요구한다.

\[
\bar E_\gamma>0,\qquad
\dot u_{\rm RCT}=\epsilon_{\rm eV}(Q-\bar E_\gamma)R,\qquad
\dot U_{\rm esc}=\epsilon_{\rm eV}\bar E_\gamma R.
\]

이때 모든 RCT primary photon은 tracked radiation field 밖으로 탈출한다고 선언하고, tracked 3-group source는 0이다. 세 에너지 항의 합은 0이다. \(\bar E_\gamma\)는 event-weighted 평균에 대응하는 **caller-supplied 조건부 모형 입력**이다. scalar 공급기로부터 유도하지 않았고, 그 값만으로 spectrum·흡수확률·momentum transfer가 결정되지 않는다. 열 항의 부호는 양·0·음 모두 가능하다. 물리적 mean-energy 상한이나 열진화 안정성까지 인증한 결과가 아니다.

API metadata는 CALLER_SUPPLIED_NO_ATOMIC_MOMENT를 기록하고, 정확한 입력값·근거는 외부 run manifest가 소유한다. 이번 독립 검산의 \(Q-1,Q,Q+1\) eV는 synthetic fixture이며 photon mean의 물리 추정치가 아니다. 원 공급기의 photon/heat/recoil moment는 계속 null이다.

향후 RCT photon을 tracked field에 넣으면 직접 전자수 변화가 0인데 primary count는 +R이므로 기존 photon inventory에 새 birth 항이 필요하다. Case-B/OTS를 이름만 붙여 대신할 수 없다.

## 실제 구현과 검증

변경은 rust/rei_microphysics 아래 src/he_rct.rs, tests/he_rct.rs, examples/he_rct_probe.rs와 src/lib.rs의 module export다. 기존 hhe_rhs, microstep, thermal은 그대로다. 새 combined_hhe_rhs와 combined_ft03_rhs의 disabled 경로는 각각 실제 baseline을 그대로 반환하고, enabled 경로는 선택된 provider와 검증된 escape-energy 입력을 함께 요구한다. FT03 wrapper는 실제 ft03_rhs의 RR·CI·DR·photo 배열을 보존한다. Ft03Model.gas만 기존 hhe_rhs에 넘겨 온도 의존 RR·CI·DR을 누락하는 오용을 회귀 반례로 검출한다.

| 증거 | 실행 결과 |
|---|---:|
| 새 native 변경영역 시험 | 24 PASS |
| 최종 crate 통합 | 116 PASS, 기존 84 + 동시 FT03 8 + RCT 24 |
| 독립 Decimal70 대조 | 12,789 checks PASS, native 호출 422회 |
| 독립 event 대조 | 96 state × 4 mode = 384회; COUNT 96, closed 288 |
| provider·경계·OFF | nominal rate 9점, 잘못된 T 8건·closure 4건·자동 source 1건 거절, OFF 16점 |
| shared provider schema | 실제 supplier thermal-rate view 2개; pinned schema의 사용 assertion 전부 검사, negative controls 40개 거절 |
| 실제 FT03 독립 추가 대조 | 212 checks PASS, 9 closed state + GM25 domain rejection 3 = native 12회 |
| 독립 검토 | 초기 confirmed 및 FT03 delta 별도 검토 기록 |

최대 gross-flux-scaled 오차는 event rate 2.924e−16, fraction rate 3.438e−16, closed energy residual 1.068e−16이다. 동결된 기준은 2e−12였다. CountOnly 출력의 null, 에너지 수지, additive RHS, source ratio 및 기존 OFF 결과를 대조했다. 전자를 재결합처럼 감소시키기, HeIII 부호 반전, 밀도 인자 누락, Q를 열과 광자에 이중 가산하는 반례를 검출했다.

공급기 nominal token은 입력 사실이다. Decimal 검산은 소비기의 수치·회계 구현을 검증하며 실제 원자율 정확도를 보장하지 않는다. Schema 검사는 설치된 범용 jsonschema 라이브러리가 아니라, **고정된 schema에 등장하는 assertion keyword만 완전히 처리하는 제한 validator**다. 그 통과도 physical admission이 아니다.

최초 native probe의 JSON format 문자열 중괄호 compile 오류는 수정했고 원 실패 로그를 보존했다. 물리식 오류와 구분되는 보조코드 구현 오류다. Cargo가 잠금파일 주석을 갱신한 사실은 기록하고 원 baseline bytes를 유지했다. Rustfmt는 복구된 도구체인에 없어 실행하지 않았다.

실행 권위는 evidence/FINAL_INTEGRATION.json, 독립 수치 결과는 evidence/INDEPENDENT_RESULT.json 및 FT03_INDEPENDENT_RESULT.json, 별도 검토 판정은 review/FINAL_REVIEW.json 및 POST_FT03_REVIEW.json이다. 추가 FT03 대조의 최대 gross-scaled 오차는 4.181e−16이다. 최초 104개 결과도 .pre_ft03로 보존했다. RCT 확장은 이번 유한 시험점만 검사했으며 기존 FT03_PRODUCT_UNDERFLOW의 전 구간 representability 계약을 자동 계승하지 않는다. Theory의 isolated-reaction 해석식·progress vector는 후속 stepper 기준으로 유도했으며, 이번에 integrated trajectory를 실행한 증거로 집계하지 않는다.

## 다음 실행과 보존 범위

**RHS wrapper를 구현한 사실은 기존 HHe 또는 FT03 implicit stepper에 RCT가 연결되었다는 뜻이 아니다.** 기존 positive BE update, endpoint thermal solve, residual, full/two-half accepted event 장부를 함께 확장해야 한다. 다음 실행 단위는 publication/RESEARCH_DAG.json의 RCT-STEP01이다. 물리 spectrum/mean-energy 지원, source spread 해소, 일반 Bianchi momentum/RT, F04 rigorous enclosure, F09 sensitivity는 별도 node다.

publication/NEXT_HANDOFF_KO.md, LOW_COST_ENTRY.json, PROVIDER_SELECTION_RECORDS.json에 exact entrypoints·수행/미수행·stop 조건을 담았다. 소비기 반환을 He 공급 스레드에 additive 문서로 연결하며, 기존 owner model lock와 source admission=false는 자동 승격하지 않는다. 기존 [160,161] 실패, strict local error<2e−4, public width<2e−3, 원 He/CR/HH 장기 연구 lane을 보존한다.

실제 Git commit은 publication/GITHUB_PUBLICATION_RECEIPT.json에서 해소한다. Drive/Dropbox의 동일 core ZIP은 source snapshot·코드·이론·CSV·검증·handoff를 포함하고 compiled target/toolchain은 제외한다. 별도 BACKUP_RECEIPT.json은 provider 완료 응답과 object ID/크기 대조를 기록하며 remote full restore와 구분한다. 백업을 되돌릴 때는 이번 새 날짜 폴더만 제거하고 이전 산출물은 보존한다.
