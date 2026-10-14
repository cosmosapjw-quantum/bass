# 실제 rei_bianchi 병목을 줄이기 위한 분석 공급 (BASS R8 병렬 작업)

2026-10-14 KST. Source는 **현재 live 작업트리**의 `research/axbi_goal_20261014/background/BACKGROUND_FAMILY_LOCK.json` SHA-256 `46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0`와 `SCENARIO_LOCK.json` SHA-256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`이다. 주어진 background는 non-tilted, homogeneous LRS Bianchi I의 **prescribed** 조건부 모델로서 $a_*=1/21$, $a_f=1/5$, $b_*=0$이다.

## 1. 화학 런타임 없이 시계 차이를 먼저 계산

$$H_F(a)=H_0\sqrt{\Omega_ra^{-4}+\Omega_ma^{-3}+\Omega_\Lambda},\quad s(a,q)=qH_F(a_*)\left(\frac{a_*}{a}\right)^3,$$
$$H(a,q)=\sqrt{H_F(a)^2+s(a,q)^2},\qquad \tau(a,q)=\int_{a_*}^a\frac{d\ln a'}{H(a',q)}.$$

이 배경에서는 $\tau(a,q)=\tau(a,-q)$가 **정확히** 성립하고, $q\ne0$에서는 $\tau(a,q)<\tau(a,0)$이다. $q\to0$에서

$$\Delta\tau(a,q)=-\frac{q^2}{2}\int_{a_*}^{a}\frac{H_F(a_*)^2(a_*/a')^6}{H_F(a')^3}\,d\ln a'+O(q^4).$$

이는 gas/ionizing network와 무관한 geometry clock이다. mpmath mp55의 직접 적분 결과는 다음과 같다.

| 동일한 $\bar z$ | $\Delta\tau(0.005)$ | $\Delta\tau(0.01)$ |
|:--|--:|--:|
| 10.2480684 | -1358.56557 yr | -5434.10474 yr |
| 6.81699117 | -1726.99341 yr | -6907.80796 yr |
| 5.80453719 | -1821.98524 yr | -7287.77439 yr |
| 4 | -1972.88341 yr | -7891.36627 yr |

실제 원 baseline ZERO/PLUS common native endpoint $a=.08873654701704167$에서 source 저장시간 차이는 $-171173626754$ 초. 배경 1D 적분은 약 $-171173626767.5603$ 초로 13.56초 차이, 관찰된 background solver/표현 오차와 양립한다. 이는 **직접 물리 재이온화 검출이 아니라 같은 prescription의 가벼운 crosscheck**다. 절대 우주 나이가 아니라 $\bar z=20$부터 경과한 proper seconds이며, $q=s_*/H_F(a_*)$와 시변 $\Sigma=s/H$는 동일한 변수가 아니다.

반환된 signed case milestone $a_{x,q}$가 도착하면 정확한 분해는

$$\tau_q(a_{x,q})-\tau_0(a_{x,0})=\underbrace{\big[\tau_q(a_{x,0})-\tau_0(a_{x,0})\big]}_{\text{background-only clock}}+\underbrace{\int_{a_{x,0}}^{a_{x,q}}\!\frac{d\ln a}{H(a,q)}}_{\text{same model, differing crossing }a}. $$

이 분해는 두 효과의 기여를 출력하도록 분석 준비에 추가할 수 있다. 둘째 항에는 완성되고 source-동일성이 확인된 actual milestone이 필요하다. `same a`와 `same elapsed proper time`을 동시에 강제하지 않는다.

## 2. 실제 ZERO의 첫 upward milestone의 조건수 진단

원 완료 ZERO의 **312238 행 전체를 검증해 저장한 정확한 10 native rows**에서

| $x_{\rm HII}$ threshold | 인접 native chord $dx/d\tau$ per Myr | $10^{-7}$ fraction / chord slope |
|--:|--:|--:|
| .1 | $6.67393\times10^{-4}$ | 149.84 yr |
| .5 | $1.82605\times10^{-3}$ | 54.76 yr |
| .9 | $2.59096\times10^{-3}$ | 38.60 yr |

위 시간 척도는 **piecewise linear reference의 국소 조건수**이고 참해의 이벤트 시간오차나 수치 정확도는 아니다. 연속적인 $|X-\widehat X|\le d$ 및 필요시 derivative lower bound가 없으면 이를 physical epoch bound로 사용하면 안 된다. 실제 first-passage bracket helper는 PR147 `milestones.py`, merged-knot PL norm helper는 PR146 `pl_metrics.py`로 이미 구현됐다. 새 helper를 중복 생산하지 않는다. 향후 numerical-error refinement를 milestone 우선으로 배분할 때 단지 어느 crossing이 작은 abundance error에도 상대적으로 민감한지 순위 정보로 쓴다.

## 3. 이미 owner가 해결한 문제와 진짜 남은 문제

- **현재 확인된 해결**: BASS_HE PR52가 보고한 `xe` vs `Ye` floor mismatch는 live reducer의 HEAD `6fe1e8d03fadbc46bdc6dd0072a55b83cbd03d0d`, source SHA `35e1499e...`에서 이미 수정되었다. 현재 `floor('xe') = 1e-7*(h+3*he)/h`이며 $h=n_H/n_b$, $he=n_{He}/n_b$. 따라서 $\delta x_e^{\rm floor}=1.243904055128545\times10^{-7}$, $\delta Y_e^{\rm floor}=9.3865\times10^{-8}$. 과거 잘못된 `xe` floor=1e-7은 **historical negative control**만으로 보존한다. 별도 외부 patch 금지.
- **준비됐으나 owner 소비 대기**: WU088_HH PR69는 서로 다른 baseline/T1 resource-only source bytes에 대한 실제 semantic source relation과10개 integration tests를 공급했다. 기존 reducer는 개별 source hash를 검사하지만 source-pair relation 적용은 owner의 완성된 PAIRED/REFINEMENT input binding에서 다시 확인해야 한다. 이 supplier를 중복 재구현하지 않는다.
- **실제 런타임 의존성**: AX07 ZERO는 조건부 $\bar z=20\to4$ 완료. AX08의 완료된 signed 5개 family + 지속 가능한 checkpoint continuation이 아직 필요. `TIME_T1_ZERO` binding/binary는 이미 존재하지만 `execution_authorized_now=false`이며 아직 RUN_NOT_STARTED. AX12 variant config도 준비됐지만 RUN_NOT_STARTED. owner에서 정한 global 2-slot·source/clock/accepted-state/space 조건을 그대로 지킨다. 준비 완료를 실행 허가나 과학 admission으로 해석하지 않는다.
- **다른 lane의 boundary**: BASS_HE의 warm P01 first-cell, HH의 stellar scattering exterior, bass_cr의 Coulomb-only kinetic substep은 여기에 원자율이나 실행 수치정확도를 이식하지 않는다. 가능한 재사용은 *잔차·참조 편향 구분과 source semantic equivalence guard* 같은 방법론뿐이다.

이 스레드는 REI active working tree에 **파일 변경·git mutation·solver start·process signal을 하지 않았다**. 새 결과는 source-consistent background clock과 ZERO 참조 조건수 계산이며, 실제 signed scientific admission을 막는 불필요한 새 gate를 추가하지 않는다.
