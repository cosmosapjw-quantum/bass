# BASS CE1-C: source/time error rounding enclosure and target geometry selection

## 결론

이전 CE1-A/B의 양의 무충돌 Bianchi-I 결합 예제에서 **정확한 이진 입력과 저장된 cubic-Hermite 경로**를 대상으로, MPFR 192비트 방향지정 반올림을 사용하는 a posteriori 오차 상계를 구현했다. 두 목표 |delta h_i|<0.0001, 1e-05은 동일한 8×16 각격자에서 각각 32개, 64개 RK4 구간을 사용해 통과했다. 이는 작은진폭 섭동해가 아니라 선택한 nonlinear 연속 운동방정식과 기록된 수치 경로의 거리를 제한하는 작업이다.

부모는 CE1-B PR232 commit 30ffc5310d3bd83549ec8f5ba6ec6f75b7701c5a다. 전용 child branch에서 작업했으며 main/owner/default native 경로는 수정하지 않았다. Scientific DAG 9/15, CE-1 PARTIAL을 유지한다.

## 정의와 가정

서명 (-,+,+,+), t는 normal proper time, u=t/T_*, ell_i=log(a_i), h_i=T_*H_i, E,P_i=(8 pi G T_*²/c²) 곱하기 에너지밀도·압력이다. Lambda=0, 대각·반사대칭 Bianchi-I, 질량 0, 충돌 없음, 양의 degree-4 초기 angular energy density와 초기 세 방향 팽창 h_i>=0인 채널에 한정한다. 초기 구면분포 F_0(q)를 고차 부분까지 유지한다.

기하학은 ell_i'=h_i, h_i'=-theta h_i+P_i(ell), theta=sum_i h_i를 따른다. 양의 초기장과 방향별 팽창은 E<=E0와 ||dP/dell||_infty <=4E0를 제공한다. Hamiltonian constraint는 초기 상태에만 부과하고 진화 중 projection하지 않는다.

## 구적·시간·초기조건의 오차를 분리

(1) Continuum pressure P(ell)와 **정확한 실수 연산으로 해석한, 저장된 이진 node·weight·density를 사용하는 P_Q(ell)**를 비교한다. F0의 degree-4 다항식과 구면 monomial 정확 적분을 이용해 binomial polynomial 부분의 차이를 정확한 유리수로 계산한다. 반올림된 노드·방위각 샘플·가중치의 모든 polynomial mismatch를 포함하며, 두 양의 binomial series tail을 MPFR RNDD/RNDU로 감싼다. 단순 fine-grid 차이로 정당화하지 않는다.

(2) 저장된 RK4 출력에서 이미 만든 cubic-Hermite path ytilde를 **정확한 이진 다항식 계수의 실수 다항식**으로 정의하고, r_ell=elltilde'-htilde, r_h=htilde'+theta(htilde)htilde-P_Q(elltilde)의 전 구간 크기를 MPFR로 감싼다. 잔차의 3차 Taylor coefficient와 기존 CE1-B의 해석적 4차 derivative majorant를 사용한다. 유리수 시간 subcell과 공간 log-scale box의 합도 float64로 먼저 더하지 않고 외향적으로 평가한다. 저장된 ray 벡터의 norm이 완벽하게 1이 아니고 sampled mass의 float64 sum이 정확한 합이 아니라는 효과도 derivative majorant에 포함한다.

(3) 동일한 이진 sx,sy와 정확한 sz=-(sx+sy), 정확한 Hamiltonian root로 정의한 reference initial h(0)와 저장된 float64 h(0)의 차이도 상계 입력으로 넣는다. 두 보증을 D+x<=y+d_ell, D+y<=4E0 x+eta_Q+d_h라는 양의 2성분 비교계에 따로 넣고 192비트 MPFR 구간 exponential/hyperbolic 연산으로 전파한다.

## 목표 선택 (u=0..1, E0=0.9, c2=.6, ct=.25, c4=.2, shear=(.2,-.13,-.07))

| angular | RK4 | h-source 상계 | h-time+initial 상계 | 합계 | 목표 | 판정 |
|---|---:|---:|---:|---:|---:|---|
| 8×16 | 32 | 6.19775012889e-06 | 1.74393282868e-05 | 2.36370784157e-05 | 0.0001 | PASS |
| 8×16 | 64 | 5.18675488262e-06 | 2.15904111226e-06 | 7.34579599488e-06 | 1e-05 | PASS |

각 상계의 값은 무차원 `max_i|Delta h_i|`에 대한 것으로, 특정 시간의 수치 참조와 차이를 측정한 값이 아니라 선택한 수학적 전제 아래의 상계다. 32구간에 비해 64구간에서는 시간 defect가 줄어들면서 source 예산이 지배적이 된다. 선택된 후보는 검사한 순서에서 통과한 사례이지 모든 해상도 중 비용 최소라는 증명은 아니다.

## 검증, 실패 분류, 엄밀성 경계

- 현재 턴의 최종 재검증: 신규 MPFR 13개와 부모 CE1-B 14개, 총 **27개 pytest PASS**. 실제 GitHub workflow에서 별도 wheel build/install·scoped test 완료 여부는 GitHub 영수증을 따른다.
- 실제 numerical candidate 재검산: 8×16 /32구간 및 8×16 /64구간, 둘 모두 exit=0. 원래 n12×24 /64구간은 exact-rational 계산 중 180초 제한시간을 넘겨 실행 실패로 기록하고 scientific failure로 해석하지 않았다. 정지한 호출을 반복하는 대신 비용이 작은 허용 후보를 사용했다.
- 초기 별도 설치 wheel smoke는 정확 십진수 3/10과 이진 float(0.3)를 혼동한 테스트에서 실패했다. 실수 근거가 아닌 테스트 구현 오류였고, Fraction(3,10)으로 교정한 뒤 CI가 성공했다.
- 종료 시 `_F.__del__`가 해제된 모듈 전역 MPFR 객체를 참조하는 오류, log-scale box를 numpy.float64로 먼저 합산하던 오류, non-dyadic subcell 경계를 이진값으로 취급하던 오류, 실제 binary ray norm과 저장 mass 합을 무시한 derivative cap을 각각 재현 후 수정했다. 수치물리식·원본 허용오차는 변경하지 않았다.
- Native Rust, production runner, non-diagonal/contracting Bianchi, 공간 변동 기하학, collisional matter feedback, arbitrary sampled angular data, input acquisition uncertainty, formally verified MPFR binding은 범위 밖이다. 소프트웨어 전체의 기계검증이나 엄밀한 physical decimal input certification을 주장하지 않는다.
- 이 결과는 **scoped mathematical enclosure evaluated with directed MPFR**, independent formally verified implementation은 아니다. 코드의 함수가 정리를 만족함을 공리적으로 가정하지 않고 수치·기저 검사를 수행했으나 독립적 전체 증명은 미수행이다.

## 결과와 다음 인계

실제 실행 코드 `bianchi/nonperturbative/einstein_interval.py`, 테스트 `tests/nonperturbative/test_einstein_interval.py`, 부모 `einstein_error_budget.py`의 source identity는 JSON 계약에 기록한다. 원본 CE1-B ZIP, S0/S1 immutable ZIP과 수치·실패·복구 로그, 단계별 증거는 본 ZIP의 parent/, evidence/에 보존한다. 전체 repository나 설치 wheel의 대체물은 아니다.

다음 과학 단위 CE1-D는 자동 실행하지 않는다. 상위 CE-1은 아직 PARTIAL, DAG 9/15, production_ready=false, merge_ready=false를 유지한다. 
