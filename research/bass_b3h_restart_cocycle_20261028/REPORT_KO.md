# B3h closed-cut restart: 조건부 구성·수치 검증 보고

상태는 NUMERICALLY_CHECKED_SCOPED_COMPANION_INDEPENDENT_ADMISSION_PENDING이다. 원 과학 결과를 반복하지 않고, 저장된 두 native 패널의 내부 절단점에서 population과 누적 사건/에너지 모멘트를 함께 복원하는 구현을 만들었다. 이는 B4 production restart나 B3i 물리 보정 완료가 아니다. 중앙 원 DAG28/88, 증분0을 유지한다.

## 조사와 선택
이전7개 저장소의1406 branch/1037 PR 전수 metadata 목록을 원 ZIP에서 복원하고, 현재7개 저장소의 최근 PR·특정HEAD 및 병렬작업을 대조했다. 현재 모든 branch의 새 pagination 및 모든 대화 원문을 전수 읽은 것은 아니다. 복원한 목록과 이번 delta는 survey에 분리했다. BASS PR211 tilted-collision memory와 겹치지 않는 원자 transaction restart를 선택했다. REC defect/tube 연구, CR parent-event native25, WU 조건부 분자 경계 및 vigilode solver restart 결과는 새로운 원자 입력으로 승격하지 않았다. 다른 branch의33/88,6/15 등 별도 집계는 더하지 않았다.

## 새 유도
population p'=b-Mp와 누적 reward z'=a+Lp를 하나의 affine block으로 확장했다. 두 구간의 state map(P,q)와 reward map(R,r)은 P2P1, P2q1+q2, R1+R2P1, r1+R2q1+r2로 합성된다. 누적 reward에 R2q1을 빼먹으면 source가 만든 population의 후속 사건 기여가 사라진다. 기본 flow 성질은 표준 Peano-Baker/variation-of-constants 결과이며 새로운 일반 정리의 독창성을 주장하지 않는다.

절단점에서 theta를0으로 되돌리는 대신 theta=theta_c+(1-theta_c)*theta_local를 유지해야 한다. exp(k*u)theta^j 모멘트에는 binomial 재기준화가 필요하다. 같은V0로 표현된 finite stock/energy에 추가 부피비를 중복 곱하지 않는다. gas와 radiation의 기하학적 work를 사건 교환과 구분하여 k=2와k=1 가중 에너지에 누적한다.

population 초기오차는 exp(-gamma*Delta)로 사라질 수 있지만 누적 reward 오차는 ell*eps*(1-exp(-gamma*Delta))/gamma로 남는다. 이 식은 같은 연산자·같은 입력의 conditional bound다. 모델/clock을 바꾸면 forcing 차이를 별도로 포함해야 한다. 상세 정의·단위·증명·gamma=0 극한은 theory/RESTART_THEORY.md에 있다.

## 실제 새 계산
새 manufactured noncommuting 모델에서 p=(1+t,2+t^2)의 해와 polynomial-exponential reward 적분을 별도로 계산하여 RK4와 비교했다. 이 p는 fixture의 양의 rescaled carrier이며 물리적 atomic fraction이 아니다. N32/64/128/256에서 최대 상태오차는9.82323133e-6,5.63850789e-7,3.37390773e-8,2.06275796e-9였다. 오차 감소비17.4217,16.7121,16.3563은4차 접근과 일치한다. N256의 최대 reward 오차는6.09247763e-10이다.

t_c=0.25,0.75,1.5초에서 실제 JSON hexadecimal checkpoint를 거친 재개 결과는 무중단 고정 격자 결과와 bitwise identical했다. 각 실행의 누적 RHS work1024를 보존했다. 이것은 adaptive-step controller나 pending journal을 포함하는 일반 B4 인증이 아니다.

QSS population reset의 최대 reward 차이는0.178348,0.126968,0.238923이며 각각 same-law 상계0.524936,0.724960,0.645219 안이다. reward clock만 reset한 대조에서는 population 차이가0이어도 reward 차이가0.639390,1.628376,1.780211 발생했다. 누적 prefix를 버리면0.510007,1.539625,3.560354의 reward 차이가 발생했다. 비가환 두 operator를 exp(sum)으로 치환한 차이는0.0387060, 순서를 바꾼 차이는0.0831436이다. 모두 fixture 범위의 실제 대조 결과다.

## 저장 native 데이터에서 확보한 새 절단 상태
native cut은 t_c=1062075.8859787965초, u_c=5.278877465967896e-8, theta_c=0.000621732884833386이다. 기존2828 endpoint tag를 두 패널로 분리하여16968개 weighted count를 조립했다.8484개 합계와 저장 기준의 최대 차이/기존 조건부 경계는1.38294980825e-15였다. 이는 독립 native 해의 정확도 개선이 아니라 같은 저장 모멘트의 재결합 일관성이다.

incoming prefix는 새 closed-form primitive로만 평가했다. N_in=5.6707393382004175, N_out=5.6853332194199175 /V0다. 저장된 전체 incoming을 보존하도록 suffix=whole-prefix로 두었으며, 옛 quadrature는 호출하지 않았다. cut의2s/2p stock과 NH*p 간 잔차는 약6.69e-67 및1.24e-66이다. 최종 atomic stock 재결합 최대 잔차4.41e-62 /V0와5-sector energy 최대 잔차3.56e-72 J/m3는 저장된 조건부 수치 경계 안이다. 이런 매우 작은 잔차를 물리 정확도로 해석하지 않는다.

같은 저장 trajectory를 suffix-local theta로 잘못 재가중하면 단일 gross tag count의 최대 차이가9870.41161794 /V0였다. 이는 clock 오결속을 분리한 계산이지, 잘못된 clock으로 native 동역학을 다시 푼 결과가 아니다. prefix를 버리면 outgoing5.68533321942 /V0를 잃는다. 해당 cut의 QSS reset 크기는7.44273725069e-29이고, source-bound 수축식의 후속 Ly-alpha count 상계는1.25435955942e-22 /V0다. 이는 상계이며 관측된 reset 효과나 물리 반경이 아니다.

## 검증·실패·경계
unit9/9, manufactured10/10, native saved-panel13/13 검사를 확인했다. 새 native ODE0회, B3i RHS0회, 옛 tests/consume/plot/quad 재실행0회다. Wolfram symbolic 항등식 검사는 성공했지만 최초 protected-symbol 오류를 보존했다. plot launcher의 권한 실패와 이후 성공 시 남은 비치명적 artifact-tool 시작 경고도 보존했다. 입력 두 파일의 hash guard를 추가했으며 계산에 쓰인 기존 bytes와 동일함을 확인했으므로 과학 계산은 반복하지 않았다.

R6/C9의 distinct-author 독립 검토는 실제로 수행하지 못했다. 따라서 이론·코드 산출물 및 serial 검증을 독립 수용으로 올리지 않는다. 이번 단위의 과학 실행 한도는 새로 고정한CPU120초/wall300초이고 과거 예산은 열거나 이월하지 않았다. 실제 계량 및 보수적 launcher debit은 BUDGET_LEDGER.json에 분리한다. source/physical/geometry/temporal/global 오차 반경은null, L4=false이며 전체 물리 완료를 주장하지 않는다.

## 산출물과 정지
코드 restart.py/native_saved.py/run_study.py, 실제 원자료와 입력핀, 제조해 reference, 실패를 포함한 실행 ledger, 새 그림2개 및 과학·시각 검토를 보존한다. 그림은180mm/화면용 진단이며89mm single-column publication 판정은 하지 않는다. R6/C9 독립 검토만 남겨 두고 새 연구 노드는 자동 시작하지 않는다.
