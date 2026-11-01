# BASS–REI F08: 새로운 전자-기하학 일치 Thomson 편광 응답

## 원본 데이터와 실계산
- REI PR349 HEAD: \`1605236b8172db411d862caa219322d6af6953b1\`.
- 원본 S0_BI 및 S0_FLRW 전자 이력: 각 16,001개 시간 표본, proper time \`0..1e13 s\`, 직접 Git blob에서 byte-exact 복사 및 SHA256 확인. REI F08 과학 승인 상태는 HOLD.
- 원본 배경: \`H_i=(1.01,0.99,1)×10^-14 s^-1\`, 평균 \`1e-14 s^-1\`, 가스 tilt=0.
- 신규 계산: 4개 원본 proper-time epoch × (8×16,16×32,32×64) angular sky = **10,752** source-electron matched model records. 독립 관측값 10,752개가 아니라 방향/시간 수치격자 표본.
- 관측지점 원래 시뮬레이션 t=1e13 s, **현대 관측자의 절대 z=0이 아님**.

| t_obs [s] | τ_T(source BI) | K [s] | 32×64 mean abs(P)/Tbar | 32×64 max abs(P)/Tbar |
|---|---:|---:|---:|---:|
| 2.5e12 | 5.087803516110597e-6 | 631211.0184513432 | 7.48698026562968e-11 | 1.2235818445970706e-10 |
| 5e12 | 9.879092820154296e-6 | 2421402.42632943 | 2.872096913890254e-10 | 4.69380913943658e-10 |
| 7.5e12 | 1.4360042537170145e-5 | 5215625.870957279 | 6.186407845758299e-10 | 1.0110319587848014e-9 |
| 1e13 | 1.854154317787376e-5 | 8868340.949340075 | 1.0519001052847265e-9 | 1.7190987894875798e-9 |

변형된 전자력 학 모델을 새로 풀지 않았다. 기존 F08 H/He 계산에서 생산된 \`n_e(t)\`를 원본 그대로 사용했다. 최초 초기 조건의 등방·무편광 **시험 흑체복사장**은 모델 가정이며 실제 REI 13.7 eV S0 광자 방출력/흡수 역사와 동등하지 않다. 따라서 원본 S0 편광 예측·Planck 관측값·생산 Einstein–Boltzmann 해라고 주장하지 않는다.

## 수학 및 검증 결과
정규화와 부호: \`(-,+,+,+)\`, \`Q=I_theta-I_phi\`, \`U=2I_theta_phi\`; \`(Q+iU)/Tbar=(c sigmaT/10) int n_e(t)t dt × sigma_ij m^i m^j + O(sigma^2,tau^2)\`. Wolfram 독립 각적분으로 계수 1/10 대조. 원본 물리 샘플로 구한 K를 직접 입사각 Thomson 산란 적분에 대입했을 때 128×256 적분 오차 \`3.2596e-9\` (상대, 한 방향), 시간 표본 16배 성긴 적분 차이 \`2.5980e-9\` (상대). \`sigma=0\`, \`n_e=0\`, 밀도 배증, 편광기저 spin-2, 가짜 원본 해시 거절, sky 전체 행 감사 포함 12개 단위테스트가 일반/최적화 각 12/12 PASS. 최초 테스트의 가짜 선형함수 \`int ne dt\` 예상 24는 수학적으로 잘못되어 실제 15로 교정했다. 물리 코드 자체를 바꾸는 수정은 아니었다. 누락된 비단조 시간·음수 밀도 인자 검사를 추가했다.

## Drift watchdog & blind referee (same-author, scoped)
- 실제 성과: 새 polarization transfer 이론 유도 + 원본 H/He n_e 이용한 수치 편광 sky와 tensor response, 기존 scalar optical-depth 단순 반복 아님.
- 치명적 한계: 시험복사장의 원래 각도/스펙트럼은 실제 S0 생성/흡수 데이터와 일치하지 않는다. \`SOURCE_ELECTRON_MATCHED != SOURCE_PHOTON_MATCHED\` 이므로 완전한 REI 편광 문제의 closure는 미완성.
- 추가 이슈: Einstein-constrained Bianchi background가 아니라 prescribed anisotropic metric; 첫 F05 원본 26-event interval과 F09 provider 결손은 독립적으로 유지. 원본 BASS KM2/PR313 P8/Peebles clock과 직접 대입 불가.
- 과도한 메타감사·확장 금지: 이 한 실계산만 Draft와 backup으로 닫고, 더 이상 source-conditional sky 변종 PR을 연쇄 생성하지 않는다.
- BASS upper 9/15 **scoped/source-mapped**; FULL PHYSICAL count unresolved, new fully complete upper +0. 중앙 REI 28/88 REPORTED; Working 33/88 non-additive; canonical +0. 기존 first tick 160/131072 BLOCKED. 이 숫자를 10,752 sky ray로 증가시키지 않는다.

## 상태
Exploratory, derived+numerically checked+implementation verified (scoped). Independent different-author referee and full real S0 radiation coupling NOT_RUN. Existing main, REI and related source owners unchanged. Production HOLD; no merge, no tolerance relaxation, no auto-next.
