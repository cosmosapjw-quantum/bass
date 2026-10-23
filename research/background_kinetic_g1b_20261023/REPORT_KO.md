# BASS G1B 연구 보고서

2026-10-23 KST. 부모 PR183의 source/과학 근거는 재사용했고 G1A의 완료 18개 이력은 재실행하지 않았다. 이 단위는 연속 FD/Planck 초기분포, 양의 구적, 무질량 radial 축약 및 V/VIII의 유한 시간 수렴 비교를 구현했다. 전체 BASS나 전체 tilted Einstein–Boltzmann solver를 완료한 것이 아니다.

## 핵심 결과

첫째, 순간 FD96 격자 source와 연속분포를 분리했다. 원 freestream.py의 clipped exponential은 그대로 보존했다. 새 FD는 momentum-decoupled 1/(exp(q)+1)이며 massive equilibrium exp(E/T)가 아니다. Planck는 별도의 massless spectrum이다. q=cp/(k_B T_ref), kappa=8piG/c^4, tau=ct/L, signature(-,+,+,+), hbar 및 k_B를 유지한다.

둘째, 모든 격자에 동일한 continuum Z_m을 적용했다. 격자마다 rho를 맞추는 재정규화를 하지 않았으므로 거친 radial 오차가 원 결과에 남는다. massive 초기 에너지 1.8, radiation .9, lambda .15는 정규화된 모형 입력이다. 임의 진폭과 고정 T_ref의 실제 평형 blackbody 조건을 동시에 주장하지 않는다.

셋째, 무충돌·무질량 특성식의 degree-one momentum flow와 degree-zero logweight로 radial 적분을 정확히 제거했다. I_p=integral q^p F(q)dq, qbar=I3/I2와 입자수 가중치를 사용하면 N^a와 T^ab를 동시에 보존한다. Planck qbar=2.701178032919063896...다. 이것은 full spectrum, I4, recoil, energy-dependent collision의 등가물이 아니다. 실제 I4와 I3^2/I2가 다르다는 대조를 포함했다. 이는 새로운 보편적 물리 정리를 주장하는 것이 아니라 해당 characteristic에 맞춘 유도와 구현이다.

## 수치 근거

고정 상태 6개에서 60개 고유 moment 평가와 66개 표 행을 생성했다. radial [4,8,12,16]은 각 부분구간 [0,4,12,24,48]의 차수이고, angular nmu=[6,10,14,20,28,40,56], nphi=2nmu다. 비교 기준은 r16/a56이며 선택한 r12/a40의 최대 비교차는 1.0870020882325667e-8이었다. 문턱에 가까운 Planck_boost의 참조만 r20/a80으로 1회 강화했고 선택 오차는 1.0916905982446595e-8, 기존 참조의 이동은 4.899770587632811e-11이었다. 허용오차 2e-8은 바꾸지 않았다. 독립 1D MP55 LRS Planck 적분과의 비교차는 2.6257077617842288e-14다.

새 coupled IVP는 16개 계획 이력과 2개 half-step 대조, 합계 18개를 완료했다. 초기 RHS에서 실패한 별도 시도 1회도 보존했다. 정상 이력은 각 33시각, tau=[0,.8]이다. V/VIII 각각 radial, angular, time 변화와 교차 fine-grid를 분리했다. 기본 DOP853 rtol2e-10/atol2e-12, tight2e-12/2e-14, max_step .04를 사용했다. default와 tight가 모두317 RHS였으므로 max_step .02의 새로운 대조2개를 추가했고 각각593 RHS였다. 동일 max-step 아래의 허용오차 비교만으로 충분한 시간 수렴을 단정하지 않았다.

선택 r8/a14와 r12/a20의 52개 core/moment/number-current 필드 비교 최대는 4.161849423977628e-9다. 두 배경 모두 최대 위치는 초기 massive 압력이다. 기하·독립 rho/flux를 포함한 core24의 최대 차이는 1.0879087761016787e-9다. angular14→20만의 최대차8.226629917607054e-13, tolerance만의 최대차1.1085257926798773e-11, half-step 전체 상태 최대차1.0097911099635831e-11이다. 여기서 error는 |x-y|/(1+max(|x|,|y|))의 유한 비교이며 순수 상대오차·전역 오차 상계가 아니다.

정상18개에서 최대 core constraint2.891848519221205e-12, kinetic constraint1.9960579241724812e-12, 독립 ledger와 입자 rho/flux mismatch6.26226363355756e-12다. time-step 대조의 잔차는 이보다 작다. coarse radial r4의 비교차1.7931097020318376e-4와 VIII angular6의2.992617440667929e-7은 실패 진단으로 그대로 보존한다. 선택 설정의 합격을 모든 격자 합격으로 바꾸지 않는다.

무질량 radial 축약 때문에 선택 격자에서 photon은392 angular carriers, massive는12544 carriers다. 총12936개가 진화한다. photon radial32배 제거는 상태수 감소이며 전체 solver32배 속도 향상을 측정했다는 뜻이 아니다. 전체 실행의 가속 benchmark는 수행하지 않았다.

## 꼬리 상계의 정확한 범위

F_F<=exp(-q), F_B<=exp(-q)/(1-exp(-Q))와 positive measure로 incomplete-gamma tail을 도출했다. 같은 처방된 geometry에서 |k|<=Kq, w/w0<=J이면 delta rho<=A_rho J(mB2+KB3)/max(mI2,I3)다. |h|<=2, ||sigma||2<=1, |a|<=.5, tau<=.8에서 K<=exp(3tau), J<=exp(7tau)를 사용한다. Q48의 단위진폭 상계 최대8.85616678612224e-14다. 실제 massive 진폭1.8에 대한 값은 RESULTS.json에 있고, Planck radial은 정확히 적분되어 생략된 radial tail이 없다.

RHS 호출에서 실제 최대 envelope는 [1.1469982284329545,.24,.25]였다. 호출점 검사는 전 구간 interval proof가 아니다. 더 중요하게, 두 self-consistent geometry는 달라지므로 이 source tail bound가 두 coupled 해 사이의 전체 오차를 인증하지 않는다. 그 안정성/오차 전달 의무는 G1C로 남겼다.

## 실패·교정·감사

첫 V_r4_a6 시도는 t=0에서 Planck pi의 대칭성 검사에 실패했다. P_ab와 P_ba를 별도 합산한 antisymmetry5.177065373618284e-18이, 거의0인 pi를 분모로 삼은 tolerance4.733165431326071e-30을 넘었다. 원 traceback과 당시 source는 evidence/curved_001 및 first_failure_source에 보존했다. 새 symmetric_bridge는 여섯 성분만 한 번 계산해 대칭으로 복사한다. 기존 vendor3파일과 허용오차는 바꾸지 않았고, positivity projection이나 density fitting도 하지 않았다. 원 실패는 물리식 반증이 아니라 floating-point representation/인터페이스 문제다.

시험은 source8개, driver최종5개로 고유13 pytest items다. 먼저 stub에서 의도적 RED를 보고 구현했다. 초기 driver4개 시험은 초기자료만 검사하고 RHS를 호출하지 않았으므로 위 오류를 놓쳤다. RHS 호출 회귀1개를 추가해 RED→GREEN으로 교정했다. 초기4개와 최종5개를 중복 합산하지 않는다.

직렬 PHYS-MATH와 PHYS-MATH-CODE 감사를 했다. source angular factor는 coordinate reflection 각각에 불변인 것이 아니라 antipodal-even임을 문서에서 명확히 했다. multiplicative occupation amplitude를 fugacity로 부르던 표현도 고쳤다. Wolfram의 exact homogeneity와 I2/I3/tail 식은 실제0/정확식이지만, infinite NIntegrate에서 overflow/underflow 경고가 있었으므로 수치 normalizer 출력은 50자리 인증으로 격상하지 않았다. 별도 mpmath·SciPy 참조가 있다. 독립 모델/subagent 심사는 NOT_RUN이다.

3개의 PNG/SVG/CSV 그림을 실제 생성하고 읽었다. 첫 fixed-state 범례가 작은 오차 곡선을 가려 위치·축 문구만 교정했고 원 그림과 동일CSV를 보존했다. 수치 재실행0이다. Python inline display의 ClientConnectorError는 저장 완료 뒤 UI 오류였고 raw/그림 생성 실패와 분리했다.

## 문헌·외부 코드·병렬 변경

NIST DLMF25.12.11,14–16의 적분 정규화와 원 arXiv1106.4807/1305.7347/1911.04937의 문제 범위를 확인했다. SciSpace 색인의 일부 연도는 원전 제출연도와 달라 원 arXiv identity를 썼다. 문헌의 cold-stream 예나 특정 Bianchi asymptotic 정리를 이 코드의 수렴 인증으로 쓰지 않았다. 현재 연구의 항등식은 직접 유도와 CAS, 구현은 source-bound 숫자 검증이다.

PR183 HEAD는 그대로였고 최신 변경분에서는 HE38 PR91이 별도 contract stage였다. 이를 gas의 현재 pi나 반응 four-force로 끼워 넣지 않았다. 이번 조사는 이전 조사에 대한 delta이며 모든 branch/대화 원문/백업을 새로 전수 읽었다는 뜻이 아니다.

## DAG와 보존

G1A finite-measure 결과는 그대로다. G1B의 S0연속 source/tail, S1양의 구적/고정상태, S2곡률 배경/시간분리/그림은 유한 범위에서 완료다. 실제 source·게시·remote backup 상태는 STAGE_DELIVERY와 최종 DELIVERY_FINAL이 소유한다. 전체 raw는 archive, 선별 source/report는 Git에 있다. 저장 영수증을 만들기 전 immutable archive에 성공 ACK를 소급 삽입하지 않는다.

다음 G1C는 같은 bounded field domain에서 source 오차가 결합 geometry/moment 해의 오차로 전달되는 정량 계약이다. 현재18개 저장 이력을 사용해 sensitivity/residual 경로부터 구성하며 전체 적분을 재실행하지 않는다. 일반 tilted smooth IC 분류, 완전한 four-force/충돌, production/restart, 전역 물리 정의역의 인증은 별도 열린 의무다. global completion percentage=null, production=NOT_ISSUED, merge=false.
