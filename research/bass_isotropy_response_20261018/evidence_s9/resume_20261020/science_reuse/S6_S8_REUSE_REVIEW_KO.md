# S6–S8 근거 재사용과 남은 물리 계약

검토 기준은 BASS PR174의 `4b30957cb008aad8019bb1a673937fc67bd017e8`이다. 이 검토는 복원된 원 source·실행 receipt·수치 분석 자료를 읽고 현재 Git blob identity와 대조했다. 과거 과학 캠페인이나 개발 테스트를 실행하지 않았다. 사용자 인계문의 `3694d6e1` 이후 S6·S7·S8 결과가 실제 존재하므로, 그 완료 범위는 재사용하고 아직 실행되지 않은 S9의 고정 여덟 이력으로 이어갈 수 있다. 실제 S9 결과에 대한 독립 검토는 그 원시 출력이 생성된 뒤 별도 기록한다.

## 1. 네 S6 의무의 실제 확보 범위

| 원 의무 | 읽은 원 근거와 확보 결과 | 남아 있는 정확한 의무 |
|---|---|---|
| Finite-d continuum angular error와 고차 moments | `evidence_s6/finite_d_r3/RETURN_S6_FINITE_D.json`: 146 rules, 1460 certificate points; series/direct 차이 최대 `1.0896141253365226e-28`, tail 최대 `1.0047069459823797e-22`; 부호 없는 상한과 저차 moment만 쓰는 S6.4 상한 검사 통과. | 계수의 비구간 고정밀 quadrature와 별도 산술 여유를 사용한 범위다. 전 구간 interval enclosure나 KL 제약 rule의 보편적 점근 정리가 추가된 것은 아니다. 원 G5의 38/344 실패를 유지한다. |
| Exact rank1 지지의 실행 가능한 certificate | `rank1_certificate.py`는 정수 이차식의 근·양성 mean·P2/P4 호환성을 Fraction으로 검사하고, 각 float ray를 폭 `2^-48`의 근 분리 구간에 결합한다. `TEST_S6_R2.log`에 22개 관련 단위검사의 실제 exit0가 있다. | 의도한 algebraic support의 exact 판정, rounded ray의 근 근접성, 최종 float moment gate는 서로 다른 근거다. Native grid에는 rank1 실행이 없었다. |
| 고정 owner spectral refinement 및 `5.369926725506957e-12` | `evidence_s6/spectral/run02_r2prereg/RETURN_SPECTRAL_REFINEMENT.json`: 원 owner `0e258464`의 57 files 불변, source deposition 26 rows, 모든 등록 gate 통과. cps 두 배 비율 16.2519, 16.0615, 16.0156, 16.0638; native−예측 최대 `2.220446049250313e-16`. | source deposition 이후 수송·흡수·진화하는 반응 이력의 spectral convergence는 다른 계산이다. S7은 한 번의 frozen-opacity slab에 대한 bin refinement를 추가했다. |
| Source-age cohort 합성과 Einstein/shear feedback | S6는 prescribed geometry의 cohort 합성·birth midpoint 2차 수렴, S7은 독립 Raychaudhuri H를 진화시키는 closed manufactured donor, S8은 전체 birth-memory tangent와 native angular refinement를 실제 실행했다. | 실제 MD14 emissivity의 물리적으로 닫힌 공급부와 native Einstein feedback, evolving reactive absorption/chemistry는 아직 구현·검증이 필요하다. |

### Angular 제약과 refinement의 구분

`CONSTRAINT_EFFECT.json`의 전체 430쌍에는 280개 개선과 150개 악화가 있다. `max(|E_P2|,|E_P24|)>1e-12`인 잡음 위 238쌍을 선택하면 기존 보고서의 **194개 개선·44개 악화**를 재현한다. 이 둘은 다른 모집단이다. 별도 held-out receipt의 30개 점근 쌍은 비율 0.780606–1.005312로 사전 기준을 만족했지만 원 G5 실패를 대체하지 않는다.

S8 `evidence_s8_native/run01/ANALYSIS.json`은 18시도 중 17측정, n_mu=256의 여섯 target 통과, 낮은 해상도의 여덟 accuracy 미달을 보존한다. `b9_n64_P2P4`는 birth11, u=0.5750000000000001에서 `INNER_P2_PRECISION_LIMIT`다. 독립 convex-hull slack은 lower `0.060849366173994196`, upper `0.006502931231664955`로 모두 양수다. 따라서 이 한 건은 **수치 정밀도 실패**이며 양의 지지 부재로 분류할 수 없다. 실제 마지막 bracket endpoint가 원 raw에 없다는 한계도 그대로 유지한다.

## 2. Spectral energy 차이의 식과 의미

원 source cell의 photon 수를 pf_s라 쓰면 비교량은

\[
\frac{\sum_s \mathrm{pf}_s\,u_s^{\rm GL8}/n_s^{\rm GL8}}
     {\sum_s \mathrm{pf}_s\,u_s^{\rm S32}/n_s^{\rm S32}}-1.
\]

고정 owner의 deposition은 GL8 cell mean을 사용하고 비교 기준은 Simpson32 cell mean이다. 저장된 40자리 기준과 panel refinement는 대략 `5.3697e-12`가 Simpson 쪽의 4차 절단 오차임을 지지한다. `5.369926725506957e-12`와 `5.369704680902032e-12`의 차이는 비율의 한 ulp인 `2.220446049250313e-16`이다. 같은 cps에서 bin 수에 따른 spread가 최대 한 ulp이고 angular spread가 0이라는 실제 행도 이 해석을 지지한다.

S7의 frozen-opacity slab에서는 bins24→48→96→192에 따라 photon/energy response 오차가 줄었고 bins192에서 각각 약 `-2.071e-8`, `-1.105e-8`이었다. 이 값은 흡수 전 inventory로 정규화한 **누적 새 cohort의 한 slab**에 대한 결과다. 원 stock의 보존 검사와 분리해서 채택한다.

## 3. Einstein 결합에서 공급부가 필요한 이유

단위는 energy density를 사용하고 `k=8πG/(3c²)`, `L0=Λc²/3`로 둔다. 일반적인 isotropic 공급부 `(U_d,p_d)`와 radiation에 대해, 기하와 물질이 다음 식을 만족하도록 구성한다.

\[
H^2=s^2+k(U_d+U_\gamma)+L_0,\qquad
\dot s=-3Hs+k\Delta P,
\]
\[
\dot H=-H^2-2s^2-\frac{k}{2}(U_d+3p_d)-kU_\gamma+L_0,
\]
\[
\dot U_d+3H(U_d+p_d)=-Q,\qquad
\dot U_\gamma+4HU_\gamma+2s\Delta P=Q.
\]

직접 미분하면 `C=H²−s²−k(U_d+U_gamma)−L0`는 `Cdot=-2HC`를 만족한다. 공급부의 손실 없이 radiation에 Q만 추가하면 `Cdot+2HC=-kQ`가 남는다. 따라서 source-age 합성 코드나 별도 photon ledger가 존재하는 것만으로 actual MD14 source와 Einstein 결합의 에너지 closure가 정해지지는 않는다.

Native가 저장한 per-H energy를 `epsilon_H`, per-H pressure difference를 `Delta p_H`라 쓰고 `n_H=n_H0/a³`를 유지하면

\[
\dot\epsilon_H+H\epsilon_H+2s\Delta p_H=q_H,
\quad U_\gamma=n_H\epsilon_H,
\quad\Delta P=n_H\Delta p_H,
\quad Q=n_Hq_H.
\]

eV/H로 반환될 때는 마지막 세 변환에 같은 eV→J 상수를 적용한다. 이 변환은 source owner를 바꾸지 않고 bridge에서 수행할 수 있다. 다음 구현에 실제로 필요한 입력은 (i) owner emissivity가 이미 fesc를 포함하는지, (ii) proper time과 다른 시간 변수의 Jacobian, (iii) 모사 spectral band에 들어가는 native energy injection, (iv) 그 에너지를 잃는 공급부의 물리적 상태와 압력/진화식이다. 이 데이터가 정해지면 Q의 중복 계상을 차단하고 energy event map과 Raychaudhuri를 연결할 수 있다. 현재 S9의 pressureless manufactured donor는 이 계약의 검증용 특정 모형이며 MD14 공급부의 물리적 선택을 대신하지 않는다.

S8의 full tangent는 고정 birth 시간·주입 amplitude와 초기 shear parameter에 대한 결과다. 기존 여덟 이력과 원 serialization failure를 보존했고 최종10/10 gate를 통과했다. 이 수용 범위와 solver-local JVP의 수용 범위도 구분한다.

## 4. 최소 문서 교정과 검증 종료

`rank1_certificate.py`의 module docstring에 있던 “binary64 this equality is undecidable”를 교정했다. Binary64 값은 정확한 dyadic rational이므로 polynomial equality는 결정 가능하다. 문제는 반올림한 ray만으로 의도한 algebraic support의 provenance를 유일하게 복구할 수 없다는 점이다. 새 문구는 exact support 검사, 근 분리 interval의 binding, 최종 floating-point moment gate를 명시한다.

실행 코드·허용오차·알고리즘은 바꾸지 않았다. Module docstring을 제외한 Python AST의 완전 일치를 확인했으며 과학 테스트를 다시 실행하지 않았다. 원 source와 전후 SHA는 `RANK1_DOCSTRING_CORRECTION.json`에 보존한다. 과거 `TEST_S6_R2.log`는 이전 동일 실행 코드에 대한 유효 근거로 재사용한다.

이번 검토의 새 계산은 저장된 통계의 구분과 문서 교정의 실행 의미 동등성 확인이다. 과학 history 실행 수는 0이며 신규 no-go 정리, production/full EoR/merge 승인을 추가하지 않는다.
