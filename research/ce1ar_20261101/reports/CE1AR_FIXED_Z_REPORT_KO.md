# BASS CE1AR | 원본 여섯 셀 Einstein–Vlasov의 고정 관측 적색이동 Sachs 거리

**연구 단위:** 2026-11-01 KST, BASS CE1AQ PR302(`bbebf7f0cdc3e23eec422f67118e8d402afb106c`)에서 원래 물리모형과 계산 파이프라인을 보존한 조건부 optical observable bridge. 이 연구는 상위 OB-1의 일부 관측함수 산출이지 완전한 OB-1 closure가 아니다.

## 1. 근거 및 보존

- 원본 물리: 양의 six-cell reflection-even massless collisionless Einstein–Vlasov, diagonal Bianchi I, metric signature `(-,+,+,+)`, `Λ=0`, 원래 8πG=1 계산 단위. 원본 물리 데이터가 사용하는 `u=t/Tstar`, `D_A` 단위 `c*Tstar`를 보존하며 결과를 Mpc 또는 실제 관측 거리로 오인하지 않는다.
- Immutable six-cell 원본 source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`, original CE1AP PR301 HEAD `baef3a4b5a556703f2e2feb93b57da6b364d29fd`; source parent `d94843f2b63638d36244d951eccdbb81f3a64357`.
- 원본 CE1AQ standalone S2 ZIP SHA256 `7b9836e71674f5a9af26dde12094ecbca5724da7f738c699de2b7ee138d9575`; S2에서 재사용한 원본 CE1AP photon geodesic CSV 16,842행 SHA256 `98bd1ed2909abfc5e47da12003354d6a3c75bee8ef0ecc13144b1a4c110a1207`.
- 원래 아홉 개 Einstein–Vlasov IVP를 재사용(GL8/16/24, epsilon=-.035,0,+.035), 신규 IVP=0. 
- 원래 observer-normal geometry `a_i^o(u)=exp(ell_i(u)-ell_i(u_o))`, `u_o=0.08`, `k_i=n_i` 공간 Killing covector, observed-normal sky 103방향을 재사용. Photon frequency/energy `E(u)=sqrt(sum_i n_i^2/[a_i^o(u)]^2)`.

## 2. 이번 연구에서 실제로 바뀐 물리 조건

기존 CE1AQ는 방출 고유시간 `u_e`를 여덟 값으로 고정했다. 이번에는 관측자가 측정한 공통 적색이동 셸 `z=0.005,0.010,0.015,0.020,0.025,0.030`을 지정하고, 각 원본 시공간/방향에서 `E(u_e)=1+z`를 Brent 방식으로 푼다. 전 방향·전 eps 모두 `z_max>=0.03333`이므로 셸 선택에 외삽은 없다. 임의 방출시각의 원래 광학 map 및 독립 Saunders determinant를 PCHIP metric interpolation과 Simpson temporal integral로 계산한다.

`A_i(u)=exp(ell_i(u)-ell_i(u_o))`, `E(u,n)=sqrt(sum_i n_i^2/A_i^2)`.

`J_ij=integral_[ue,uo] du [delta_ij/(A_i^2 E)-n_i n_j/(A_i^2 A_j^2 E^3)]`.

`G=(A_e J b)^T (I-s_e s_e^T)(A_e J b)`, `D_A/(cTstar)=det(G)^(1/4)`, independent Saunders `D_A=a_e sqrt(a_e E_e sum_cyclic(n_k^2 I_i I_j))`, `I_i=integral du A_i^2/(a^6 E^3)`.

**고정 적색이동 source variation:**

`[d_epsilon D_A]_z = [d_epsilon D_A]_{ue} - (partial_ue D_A) [d_epsilon ln E]_{ue}/(partial_ue ln E)`.

이번 데이터의 derivatives는 epsilon +/-0.035 중앙 secant이고, 완전한 epsilon→0의 엄밀 tangent 또는 remainder bound를 뜻하지 않는다. 궤적 emission-clock shift는 `due/depsilon= - (d_epsilon ln E)/(partial_ue ln E)`이다.

## 3. 실제 새 물리 데이터와 대표 수치

GL8/16/24 × epsilon 세 값 × 관측 redshift 셸 여섯 개 × sky 103방향 = **5,562 new fixed-z physical ray/area records**, sky source response **1,854 records**, 합계 **7,416**. 이는 기존 9,888 CE1AQ 고정시간 행을 다시 센 것이 아니라 다른 관측 조건의 새 계산이다. 기존 9 Einstein IVP는 전부 재사용했다.

GL24 z=0.020, epsilon=0에서:

| 방향 | D_A/(c Tstar) | equal-volume isotropized proxy 대비 | epsilon 중앙 source response (고정 z) | 고정 방출시각 직접 항 | 방출시각 이동 항 |
|---|---:|---:|---:|---:|---:|
| x | 0.0280441696266747 | -25.459979% | -7.01485665e-9 | -9.77407639e-11 | -6.91711683e-9 |
| y | 0.0486053915886009 | +29.190736% | +1.62837065e-9 | +2.86417715e-11 | +1.59972700e-9 |
| z | 0.0426021525629319 | +13.234422% | +1.10889973e-8 | +1.82709601e-10 | +1.09062910e-8 |

**물리적 해석:** 이 원본 조건부 Bianchi-I 모델에서는 고정 관측 적색이동 조건의 방출시각 이동 항이 세 축의 직접 광학 항보다 크다. 이것은 실제 관측 CMB/SN 데이터나 관측 우주의 shear 수준에 대한 결론이 아니다. 위 equal-volume isotropic 비교는 동일 원본 시공간의 부피 스케일인자로 만든 **운동학적 대조**, 별도 Einstein–Vlasov FLRW 해가 아니다. 원본 shear 및 Delta D_A의 물리적 관측가능성은 여기서 결정하지 않는다.

## 4. 수행 검증 및 claim ceiling

- 로컬 `pytest`: **13/13 PASS**. 출처 메타데이터 위조 거절, redshift monotonicity / outside-horizon rejection, 6×3×3×103 source count, source-response implicit correction, FLRW constant-H exact `D_A=z/[H(1+z)]`, 방향별 양의 beam determinant, 동일 입력 GL16/24 교차 비교 및 integration panel self-comparison.
- GL24 max fixed-z root |z(recovered)-z_target| = `7.77156e-16`; max Jacobi–Saunders relative gap = `1.14379e-15`; max implicit total-vs-direct finite source secant absolute gap = `3.55062e-14`. GL8/16에서도 같은 범주.
- 같은 작성자의 원래 CE1AP SHA 소스만으로 별도 축방향 광선해를 구현하고, 162개 원본 axis redshift/distance rows를 독립 `scipy.integrate.quad`로 검증: 162/162 PASS, max absolute distance `9.29812e-16`, max emitter clock diff `1.52656e-16`. 고의 axis swap 부정 검사에서 D_A gap `0.0205612` 검출.
- 숫자 적분의 동일 grid 간 agreement는 8/16/24 원본 모델 동일성의 제한 검증이지 광학 연속극한 또는 엄밀 error enclosure가 아니다. S2 원본 byte identity와 새 수치 output numeric identity는 별도로 보고한다.
- 새 데이터의 약 25% 수준 축방향 거리 비등방성은 사용자 지정 강한 이방 모델의 내부 수치일 뿐, 실제 ΛCDM/Planck 적합 결과를 뜻하지 않는다.
- 미수행: distinct-author R6/C9, 측정된 full observational likelihood, source-matched recombination/visibility, REI IGM H/He source, fully coupled CE-1/OB-1, time/angular continuum enclosure, production migration.

## 5. DAG 및 연구 정책 반영

BASS upper **9/15 scoped/source-mapped**, **new completed upper 0**, CE-1 PARTIAL, KM-2 PARTIAL, OB-1 not closed. `OB1_partial_observable_fixed_z=NUMERICALLY_CHECKED_SOURCE_CONDITIONAL`만 기록. 다른 REI 28/88, VigilODE 7/23을 이 분모에 합산하지 않는다. 별도 BASS governance Draft PR305의 science-first 목표(고정 관측 적색이동 관측량)를 구체적으로 실행한 단위이며, PR305 자체를 부모 science branch에 merge하지 않는다.

Production readiness false, merge readiness false, auto-next false. 다음 단위 후보는 fixed-observed-z **matched physical FLRW owner** 또는 source-consistent opacity+visibility, 실제 관측 likelihood와 source interface가 어느 DAG 소유인지 확정한 뒤 하나만 선택한다. 다른 closure의 KM2O/REI를 자동으로 합치지 않는다.
