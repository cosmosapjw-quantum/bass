# S8 그림 검토 마감

## 판정과 검토 대상

기존 실제 출력 그림에 대한 08 hostile audit와 07 residual pass를 순서대로 수행한 결과는 **PASS_SCOPED_ACTUAL_IMAGE_AUDIT**다. 180 mm 네 패널 요약 PNG와 90 mm 개별 PNG 네 개를 실제로 열어 확인했다. 기존 그림 10개(PNG 5개·SVG 5개), provenance의 source 21항목(고유 경로 20개), 원자료 압축 해제 바이트가 모두 기록된 크기·SHA-256과 일치한다.

생성 시점의 `FIGURE_PROVENANCE.json`은 당시의 pending 상태를 보존한다. 이번 `FIGURE_AUDIT08_07.json`이 그 미완료 시각 검토를 닫는다. 그림 재생성, 과학 계산 재실행, source·preregistration·DAG 수정은 0회다. 원 실행의 physmath 1.3.0 provenance는 보존했고, 이번 기록 마감에는 사용자가 지정한 1.0.0의 근거 재사용 규약을 적용했다.

## 의미 검토

A 패널은 초기 signed shear `y0`에 대한 해석적 접선을 실제 대칭 비선형 유한차분과 비교한다. joint(h,b,y) 최대오차와 b 최대오차가 같아서 두 선이 겹치며, 열린 원과 채운 사각형이 실제 중첩을 표시한다. Richardson 오차 `1.0230571945157863e-10`과 가장 작은 유한차분 간격의 joint 오차 `2.287956546498382e-6`는 별도로 기록했다.

B 패널의 세 생략 대조군은 각각 birth memory, `mu_b`, `alpha_b` 항의 기여를 확인한다. 판별선은 `max(1e-5,100*full_y_FD_error)=1.1293536544831895e-5`이며, 세 대조군이 모두 이 선을 넘는다. 표시된 부호 있는 `alpha_b`는 양의 물리적 가중치의 미분이다.

C·D 패널은 새 광자만의 `A_new=DeltaP_new/U_new`에 대한 각도 오차를 같은 축으로 비교한다. 목표선은 기존 `1e-6`이고, 낮은 해상도에서 측정된 새 실패 8개와 과거 n32 측정 실패 4개를 유지한다. b0=0.9,n64,P24의 수치 실패는 별도 status strip의 + 기호, 과거 n32의 두 support 실패는 x 기호로 표시한다. 누락된 행에는 가상의 오차를 배정하지 않았다.

원 tangent run01의 `numpy.bool` 직렬화 오류와 exit 1은 캡션에 남아 있다. 그 뒤 별도 게시한 resume가 기존 적분 7개를 SHA로 재사용하고 남아 있던 gauge 적분 1개만 수행했다. Native 전체 integrity 실패와 n256 여섯 정확도 목표 통과도 별도의 결과로 유지한다.

## 가독성 및 배치

모든 제목·축·tick·범례·수치 annotation을 실제 PNG에서 확인했다. 잘림이나 핵심 정보의 겹침은 발견하지 않았다. Native 계열은 색 외에 원·사각형·삼각형을 사용한다. 네 패널 요약본은 180 mm로, 개별 패널은 90 mm로 사용한다. 범례의 열린/채운 marker 및 status strip의 x/+ 의미를 제공된 캡션과 함께 전달하면 된다.

현재 네 패널 요약과 개별 패널 구성을 유지한다. 수정이 필요한 P0/P1 결함이 없어 그림·캡션·plotter를 바꾸지 않았다. 원 실행의 과학적 판정은 각 execution receipt가 소유하며, 이번 PASS는 그림과 원자료의 일치 및 가독성에 대한 판정이다.

## 고정 식별자

- Plotter: `53899baaae2cd5d4e2fddafbb317af9559001f0775632a93c8261c324f2b0080`
- 요약 PNG: `df8d29589003592b053020e342fcc45b5ac793adc48f9c2b214f13d280790bc1`
- 요약 SVG: `8b2f49d94244c40e06b5c2e34c656b731f625e18137602775e3671e1d2bd2df0`
- Plot data: `c1ce453234ebda886a1803449fe3f7450b03dba68e8eceb88671f96b8587e710`
- 원 생성 provenance: `b7734741979f20488d8957f54db7644553b2499c0fbb4052dc072a34ff04c593`
- Tangent 최종 return: `65319f6d6598af4565d6246b3fca5068f03c8f8c7ff479a0e9182831c3b6893d`
- Native 원자료: `e72fe3952929f63333872627e0d76e30c489c9e7f8f141d4fd79ca28f3a26e09`

