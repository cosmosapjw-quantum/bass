# Phase B — 실제 실행 전 고정 구현

Root CODING_CONTRACT_PHASE_B.md의 constant-left non-Lyα activity-ratio 모델을 구현한다. 저장된 admitted Phase A JSON만 읽으며 Phase A source 함수·기존 native/inverse/tube/result는 호출하지 않는다. 원 311-bin table와 saved coefficients의 binary64 값은 MP70으로 정확히 lift한다. 새 channel_maps_b는 gross affine map을 먼저 만들고 그 stoichiometry로 M,b를 정의한다. Virtual C/source를 양수식으로 재조립하고 diffusion edges를 한 번만 계상한다.

finite_b는 실제 old incoming packet의 exact binary h/eta0/상수와 mp.log(Es/E)에서 두 smooth 구간과 A를 직접 구성한다. 이전 reference.evaluate를 호출하지 않는다. 저장65자리 Nin/Uin/duration은 재사용하며 halfdecimalunit는 문자열 표현 반올림만 뜻한다. 이전 quadrature/source remainder는 null, 과거2e-11은 acceptance tolerance이고 엄밀오차가 아니다. 새 bounds는 저장 moment numbers와 명시된 MP arithmetic allowance에 조건부다.

K b−K² b_s+K³ b_ss의 endpoint particular와 homogeneous layer의 contraction을 보존한다. 생략 layer는 실제 log exponent와 bound를 기록한다. 실제 incoming knot에서 population과 error bound를 이어간다. Unweighted Ip는 endpoint storage를 포함한 정확한 moment identity에서 계산하고, k1은 old incoming energy, k2는 새 적분을 쓴다. 새로운 clock/Bprime/k2 integrals는 독립 MP16/24 Gauss 및 analytic Cauchy sup/Taylor remainder와1e-55 gross arithmetic allowance를 기록한다.

owners_b는 MP event counts로 ground/interface/continuum/electron 재고와 atomic/gas/ambient/Lyα energy owner를 업데이트한다. PL departure×E³는 다항식 적분, Wien term은 닫힌 antiderivative, Planck−Wien 차이는 positive exponential series와 geometric tail로 계산한다. 각 spectral bin의 linear+Wien 함수는 endpoint/실제 interior critical point에서 positivity를 확인한다. 선택 Lyα shell은 이 공유 ambient spectrum에서 한 번만 제거한다.

같은 사전 검토에서 root가 승인한 교정을 반영했다. Gas/ambient의 throughout-step debit margin에는 exp(2h)/exp(h)를 적용한다. Weighted count bounds는 sector energy bounds와 endpoint positivity에 전파한다. Geometry work는 exp(3h)로 final right densities를 공통 V0 에너지로 바꾼 뒤 별도의 adiabatic 식으로 계산한다. Dust/internal work는0이다. Event energy와 right density를 직접 빼는 혼합 단위식은 쓰지 않는다.

에너지 단위는 root의 최종 source-binding 교정대로 old native_cosmology.EV_J의 exact binary64 lift를 모든 Phase B 채널과 E21_J에 공통으로 사용한다. SI exact decimal 정의와 상대 표현 차이를 별도 기록하며 old U 값을 재적분·rescale하지 않는다. Native stimulated/spontaneous 표기 및 omitted hard-stimulated scope도 result에 보존한다.

Transaction checks가 통과한 후 보존한 vendor/core.py의 core.rhs를 새 five-sector packet에 정확히 한 번 호출한다. 보존한 geometry.si_to_core와 FixedScale(length1m)을 사용하고 모든 source 동적 quantity를 old history로 수출했다고 주장하지 않는다. T는 right proper-volume energy density, cQ는 공통 event energy/saved duration/exp(3h), Q0=cQ0/c이며 각 isotropic sector pressure를 따로 둔다. 독립 isotropic algebraic RHS와 각 nonzero own scale에서5e-12로 비교한다.

명령은 unit root에서 `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python code/metered_b.py phase_b`다. 기존 wrapper/Phase A freeze는 불변이다. 새 wrapper는 동일 cumulative ledger와60CPU/180wall/768MiB/1thread allocation을 debit한다. 새로운 core call은 transaction검사 전0, 검사 후1이며 실패해도 자동 replay하지 않는다. 실패와 raw partial JSON/stdout/stderr/exit/cost는 보존한다.

Python3.12.14, mpmath1.3.0, numpy2.3.5의 기존 환경을 사용한다. 구현 준비 중 새 package 설치나 과학 테스트는 실행하지 않았다. 새 scientific run은 root의 실제 S1A backup ACK와 Phase B 실행 지시 후 final freeze에서 한 번만 수행한다. Requested model은gpt-6.1-sol, actual runtime model은노출되지않아null이다. Original DAG27/88, physical radii와 total inherited physical/input error는null을 유지한다.
