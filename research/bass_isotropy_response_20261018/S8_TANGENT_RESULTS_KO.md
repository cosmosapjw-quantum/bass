# S8 full birth-memory tangent: 실제 결과와 재개 마감

## 결과

**초기 signed shear `y0`에 대한 full birth-memory tangent가 사전 등록한 10개 최종 gate를 통과했다.** 기존 해석 접선 적분 1회와 대칭 비선형 적분 6회를 그대로 재사용하고, 아직 실행되지 않았던 source-frame gauge 적분 1회만 추가했다. 계획된 적분은 총 8회 완료되었으며, 과거 적분 재실행은 0회다.

이 결과는 양의 P2/P4 보정을 적용한 새 birth와, 초기부터 존재하는 isotropic·physical anisotropic 광자 분포를 함께 가진 closed manufactured donor+radiation+Lambda 모델에서 얻었다. 기본 입력은 `n_mu=16, K=32, b0=0.3, y0=0.08, x_end=1.2`이고, 접선 미분에서는 birth 시간과 그 밖의 입력을 고정했다. 기존 광자 분포는 원래 가중치와 방향을 보존한 채 수송한다.

Non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`를 유지했다. 코드의 `h=H/Hstar`, `y=s/Hstar`를 사용하면 `Sigma=sqrt(3)|y|/h`다. 전체 실행 조건은 `evidence_s8_tangent/PREREGISTRATION.json`이 소유한다.

## 해석 접선이 포함하는 기억 항

각 birth의 `delta b_u`를 저장하고, 현재 수송 차이 `d=b(x)-b(u)`의 변분과 birth 때 결정한 방향·가중치의 변분을 함께 전파했다. 한 cohort의 각도 합에 대해

\[
\delta\!\left[\sum_i \alpha_i R(d,\mu_i)\right]
=
\sum_i \alpha_i R_d\,\delta b(x)
+
\sum_i\left(\alpha_{i,b}R+\alpha_iR_\mu\mu_{i,b}-\alpha_iR_d\right)\delta b_u .
\]

를 사용하며, anisotropic stress에는 `R`을 `D`로 바꾼 같은 구조를 적용한다. 고정 source 시간과 양의 내부 KL 해에서 유도한 접선으로서, `mu_b`, `alpha_b`, `delta b_u`가 서로 다른 항을 담당한다. `alpha_b`의 부호는 물리 가중치의 양성 조건과 구별된다. 구체적인 유도와 KL 공분산 방정식은 기존 S8 이론·코드 문서와 고정 source에 남아 있다.

## 실제 비선형 유한차분 비교

`epsilon=0.02,0.01,0.005`의 세 대칭 비선형 쌍을 사용했다. 아래 값은 `x>=0.2`에서 해석 접선과 중앙 유한차분의 최대 절대 차이다.

| epsilon | h 오차 | b 오차 = joint(h,b,y) 오차 | y 오차 |
|---:|---:|---:|---:|
| 0.02 | 3.3987609070473823e-6 | 3.660123369392254e-5 | 1.8066242317704706e-6 |
| 0.01 | 8.497944080643194e-7 | 9.15152258423868e-6 | 4.5172438278839877e-7 |
| 0.005 | 2.124550934068381e-7 | 2.287956546498382e-6 | 1.1293536544831895e-7 |

간격을 반으로 줄인 두 비율은 b와 joint에서 각각 `3.9994693076493584, 3.9998673044051856`, y에서 `3.999394986426375, 3.9998487718633644`다. 중앙차분의 2차 수렴비가 사전 gate `[3.5,4.5]` 안에 들어왔다.

가장 작은 두 간격의 Richardson 외삽 오차는 h `8.655187677675258e-12`, b `1.0230571945157863e-10`, y `5.967948357721298e-12`다. h,b,y 최대값은 `1.0230571945157863e-10`으로, 사전 목표 `1e-8`을 통과했다. 가장 작은 간격 자체의 joint 중앙차분 오차 `2.287956546498382e-6`도 별도 사전 기준 `2e-5`를 통과했다. 중앙 유한차분 오차와 Richardson 외삽 오차를 별개로 보존한다.

## 세 생략 대조군

가장 작은 실제 비선형 유한차분의 y 응답에 대한 차이로 각 생략 항을 시험했다. 판별선은 기존 절대 기준과 full 접선 오차의 100배 중 큰 값,

\[
\max(10^{-5},100\times1.1293536544831895\times10^{-7})
=1.1293536544831895\times10^{-5}.
\]

다.

| 생략한 항 | 최대 y 오차 | full 접선 오차의 배수 | 판정 |
|---|---:|---:|---|
| birth memory | 0.005604466821960211 | 49625.43663547895 | 사전 기준으로 기각 |
| mu_b | 0.004221625901789941 | 37380.90265198483 | 사전 기준으로 기각 |
| alpha_b | 0.004206095301310206 | 37243.3850513813 | 사전 기준으로 기각 |

여기서 `omit_birth_memory`는 kernel shift의 `-R_d delta b_u`와 `-D_d delta b_u` 항만 생략하고 `mu_b`·`alpha_b` 항을 유지하는 대조군이다.

이 입력에서는 세 항 각각을 빼면 실제 비선형 응답과의 일치가 소실된다. Birth 때의 moment admission과 그 뒤에 전파되는 미분 응답을 각각 검증해야 한다는 점을 직접 수치로 확인했다.

## 보존·양성·고정된 초기 광자장

| 검사 | 실제 최대값 또는 결과 |
|---|---:|
| 8개 적분의 Hamiltonian 상대 잔차 | 1.1364128943362259e-13 |
| cohort 에너지 상대 잔차 | 3.02558478124882e-15 |
| event 에너지 상대 잔차 | 2.1558497777419566e-16 |
| 선형화 제약의 scaled 잔차 | 1.0489191719766415e-14 |
| 선형화 제약 전파의 scaled 잔차 | 1.0067142588549513e-16 |
| cohort별 접선 에너지 상대 잔차 | 3.813235559021515e-16 |
| source event 접선 에너지 scaled 잔차 | 9.972862005348015e-18 |
| birth moment 미분 잔차 | 2.0816681711721685e-16 |

P24 birth는 224개이며, exact stored-binary64 `M2`와 `M4`가 각각 224/224 통과했다. 최대 절댓값은 `|M2|=1.5984037391100876e-16`, `|M4|=1.0178236206626163e-15`로, admission은 기존의 정확한 `3/10^15`를 유지했다. 최소 양의 가중치는 `0.03446377610335262`였고 reflection weight·direction 오차는 저장된 값에서 모두 0이다.

KL 공분산의 최소 고유값은 `0.10024163508226619`, 최대 condition number는 `1.996416296797181`이었다. 이 실행에서 확인한 미분은 이 양의 full-rank 내부 영역에 속한다. 초기 광자 분포 두 개의 digest는 8개 적분에서 모두 일치하며, 물리적으로 anisotropic인 기존 source를 다시 보정하지 않았다.

Source-frame GL gauge 검사는 8개 birth를 별도로 가진 1개 적분이다. 기록된 `delta h=delta y=0`, `delta b=1`의 최대 잔차와 선형화 제약 잔차가 모두 0으로 나왔다. 고정 coordinate grid의 b0 변화와 source-frame gauge 이동은 실행 계약에서 구별한다.

## 실패와 생산적인 재개

원 run01은 7개 적분을 완료한 뒤 `assessment.gate_results.richardson_accuracy`의 `numpy.bool`을 JSON으로 쓰는 과정에서 **exit 1**로 종료했다. 실패 종류는 **구현 / 직렬화**이며 원 로그·process receipt·완료한 raw JSON 7개를 보존했다.

별도 게시한 resume는 이 boolean을 직렬화 가능한 값으로 변환하고 기존 raw의 SHA를 확인하여 유한차분 평가를 복구했다. 추가 계산은 원래 미실행 상태였던 gauge 적분 1개다. 물리 방정식, 수치 허용오차, 기존 실행 바이트를 바꾸지 않았다. 원 실패를 성공으로 덮어쓰지 않고 resume의 10개 gate 통과를 별도 결과로 기록했다.

원 과정 wall time은 `9.801321730999916 s`, resume 과정은 `1.0206910599954426 s`다. 합계 `10.822012790995359 s`, 최대 process RSS `84424 KiB`, worker 1개였다. 기록된 raw JSON 총량은 `1896664 bytes`다.

## 사용 범위와 남은 의무

이번 결과는 closed manufactured donor 모델에서 양의 KL birth 해의 매끄러운 내부 영역에 대한 full birth-memory tangent를 검증한다. Feasibility 경계와 rank 변화에서의 미분, 유한 stopping branch 자체의 미분, 실제 MD14 spectral-owner feedback을 결합한 접선은 후속 의무다. Native finite-bin photon/energy ledger와 continuum angular·spectral accuracy는 각자의 원자료와 기준으로 검증한다. 기존 native 각도 캠페인의 낮은 해상도 실패와 수치 실패는 별도 native 결과에 유지한다.

이 문서는 완료된 산출물의 결과 집계이며 새로운 적분·test를 수행하지 않았다. 기존 S8 연구의 physmath 1.3.0 기록은 유지하고, 이번 결과·그림 마감에는 현재 지정된 1.0.0의 근거 재사용 규약을 적용했다. PR은 draft로 유지한다.

## Source와 결과 식별자

- Repository: https://github.com/cosmosapjw-quantum/bass
- PR174: https://github.com/cosmosapjw-quantum/bass/pull/174
- 원 7개 적분 source: `4508e5de9a9f2c5ad1fc7c9a9f53983305e8f613`
- resume 분석·첫 gauge source: `2e6b4a150559b0bea52938896a901f6d438f3582`
- 원 preregistration SHA-256: `6f88cac768b78c324705590bf6a7e5b2912311f3a4c9494d958a1e4ed2c2ba58`
- resume preregistration SHA-256: `0fefa71f865961400c05a071c9c83ef07f2baceb1845cfe789384892c3a62631`
- `evidence_s8_tangent/resume_r2/RETURN_S8_TANGENT_R2.json` SHA-256: `65319f6d6598af4565d6246b3fca5068f03c8f8c7ff479a0e9182831c3b6893d`
- `evidence_s8_tangent/FINAL_TANGENT_SUMMARY.json`: 원자료·process receipt 해시, 8개 적분 집계, 자원 측정과 gate 결과를 포함한다.
- `evidence_s8/figures/run01/S8_SUMMARY_180mm.png` 및 개별 90 mm PNG/SVG: 실제 출력 그림.
- `evidence_s8/figures/run01/FIGURE_AUDIT08_07.json`: 원자료 일치와 실제 이미지의 08→07 검토 마감.

