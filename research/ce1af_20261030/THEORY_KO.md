# BASS CE1-AF | 원래 six-cell Einstein–Vlasov에서 전단-복사 교환과 l=2↔l=4 모멘트 위계

2026-10-30, parent isolated Draft PR #283 `50d417cb6ab9c50feaafda594a539dcbb8e2dce2`.

## 물리 계약과 출처
- 대각 Bianchi I, signature (-,+,+,+), Λ=0, 무질량 무충돌의 양의 reflection-even six-cell 분포 `U₀(n)`; original source SHA256 `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035`. 초기 shear `(0.2,-0.13,-0.07)`는 고정된 exact dyadic. `u=t/Tstar∈[0,2/25]`, `ell_i=ln a_i`, `h_i=ell_i'`.
- 모든 E,P,R는 원래 BASS Einstein-ODE의 **무차원 정규화**이다. SI로 환산하면 `E=8πG Tstar² ρ_energy/c²`, `P_i=8πG Tstar² p_i/c²`와 동등한 표기를 쓸 수 있지만 여기서는 c나 Tstar를 1로 재정의하지 않는다. 물질 flux와 방향 비등방 stress는 normal-frame.
- 기존 CE1-AE의 정량 l=4 연속시간 kernel과 별개이며 이를 재인증한다고 주장하지 않는다. 원래 upper DAG는 9/15, 21 edges, CE1 PARTIAL, scoped R/C 18/20, 새 상위 완료 노드 0.

## 1. 정확한 Liouville–Einstein 연결

보존 공변 운동량 방향 `n`에 대해

\[
 Q=\sum_i n_i^2e^{-2\ell_i},\quad r=\sqrt Q,\quad x_i=\frac{n_i^2e^{-2\ell_i}}Q,\quad V=e^{-\ell_1-\ell_2-\ell_3}.
\]

\[
 E=V\int U_0 r\,d\Omega,\quad P_i=V\int U_0 r x_i\,d\Omega,\quad R_{ij}=V\int U_0 r x_ix_j\,d\Omega.
\]

`Σ_i x_i=1`, 따라서 정확하게 `ΣP_i=E`, `R_ij=R_ji`, `Σ_j R_ij=P_i`, `R` positive semidefinite. `θ=Σ_i h_i`, `h_i'=-θh_i+P_i`, `ell_i'=h_i`.

\[
 \frac{r'}r=-B,\quad x_i'=2x_i(B-h_i),\quad B=\sum_j h_jx_j.
\]

다항 시간 미분은 다음 두 exact closure를 준다.

\[
 \boxed{E'=-\theta E-\sum_jh_jP_j},\qquad
 \boxed{P_i'=-(\theta+2h_i)P_i+\sum_jh_jR_{ij}}.
\]

이는 `∇_a T^{ab}=0`의 Bianchi I normal-frame 에너지 방정식을 표본마다 직접 구현하며, **사중극 압력의 변화율이 네 번째 각도 모멘트에 결합**함을 보여준다. `R_ij`는 l≤4 원천에 의존하며 압력만 알고서는 일반적으로 닫히지 않는다.

## 2. 사중극자 압력, 전단 구동과 교환 법칙

`H=θ/3`, `σ_i=h_i-H`, `Π_i=P_i-E/3`, `Σσ=ΣΠ=0`. Einstein 방정식에서

\[
 \boxed{\sigma_i'=-3H\sigma_i+\Pi_i}.
\]

복사-전단 work `W=Σσ_iΠ_i`와 `Sσ=(1/2)Σσ_i²`에 대하여

\[
 \boxed{E'+4HE=-W},\qquad \boxed{S_\sigma'+6HS_\sigma=+W}.
\]

`E+Sσ=3H²` (Hamiltonian constraint)이며 `W`는 양쪽 방정식에서 정확히 서로 소거된다. 일반적으로 W의 부호는 고정되어 있지 않다.

정지 관측자의 positive bolometric fractional sky에서 Condon–Shortley convention의 reflection-even real spherical harmonics

\[
 Y_{20}=\sqrt{5/(16\pi)}(3s_z^2-1),\qquad
 \Re Y_{22}=\sqrt{15/(32\pi)}(s_x^2-s_y^2)
\]

과 `α_{2m}=4πa_{2m}/E`를 사용한다. `w_i=P_i/E`, `q0=3w_z-1`, `q2=w_x-w_y`이면

\[
 \alpha_{20}=4\pi\sqrt{5/(16\pi)}\,q_0,\qquad
 \alpha_{22}=4\pi\sqrt{15/(32\pi)}\,q_2,
\]

\[
 \boxed{\frac{W}{E}=\frac{1}{2}[\sigma_zq_0+(\sigma_x-\sigma_y)q_2]}.
\]

`C2_fractional=(α20²+2α22²)/5`이며 이것은 실제 온도 `C_l`이나 ensemble CMB covariance와 다르다.

## 3. 평균 팽창에서 분리된 복사 에너지 관측량

`\bar\ell=(\ell_1+\ell_2+\ell_3)/3`, `\bar\ell'=H`. 위 정확한 에너지 교환식을 적분하면

\[
 \boxed{\log\frac{E(u)e^{4\bar\ell(u)}}{E(0)}=-\int_0^u\frac{W(v)}{E(v)}\,dv}.
\]

이 식은 부호 없는 항등식이며 full-horizon `W>0` 보편정리를 뜻하지 않는다. `W/E`는 차원 없는 u 단위의 에너지 교환률이고, 위 비는 평균체적 redshift 효과를 제거한 상대 복사 에너지다.

## 4. 원래 continuous six-cell의 초기 shear work 엄격 부호

`u=0`의 `r=1`, `x_i=n_i²`. µ=|n_z| cell `[0,1/2],[1/2,1]`과 t=2φ/π cell `[0,1/4],[1/4,3/4],[3/4,1]`에서 원래 이진유리수 셀 에너지를 정확한 분수로 해석한다. 각 µ cell에서 `<µ²>=(µ₀²+µ₀µ₁+µ₁²)/3`. φ cell의 `<cos² φ>`는 `[1/2+√2/π,1/2,1/2-√2/π]`.

따라서 `E0=Σe_ij`, `Pz0=Σ e_ij <µ²>_i`, `D=Σ_i (1-<µ²>_i)(e_i0-e_i2)>0`, `Px0-Py0=2√2D/π`. `s=(sx,sy,sz)`인 초기 shear에 대해 정확히

\[
 W_0= A+B\frac{2\sqrt2}{\pi}D,
 \quad A=\frac{s_x+s_y}{2}(E_0-P_{z0})+s_zP_{z0},\quad B=\frac{s_x-s_y}{2}>0.
\]

기하학적 유리 부등식 `sqrt2>7/5`, `π<22/7`으로, exact Fraction 계산에서 `W0>0.007175>0.007`을 얻는다. 이 엄격 하계는 **초기 시점 원래 continuous six-cell source**에만 적용한다. GL에 대한 전 시간구간의 `W>0`는 수치적 관찰이며 엄격한 부호 인증은 미수행.

## 5. 구현·검증·해석 범위

`source/shear_work_physics.py`는 원래 source 함수의 GL6/8/16/64 positive ray weights를 그대로 사용하여 401 시점씩 **4×401=1,604 실제 6D self-consistent Einstein–Vlasov solution states**를 생성한다. 43개 칼럼에 E,P,R,h,σ,Π,α2,C2,W,Sσ, 누적 shear work와 Hamiltonian/log balance를 저장. `source/certify_initial_shear_work.py`는 GL을 호출하지 않고 six continuous cells의 최초 모멘트만 exact rational 계산한다. `source/plot_ce1af.py`는 앞선 CE1-AE SHA-locked C4 data와 새 C2를 함께 시각화한다.

**증거 수준:** 보존식과 전단 변환은 `derived`, Wolfram 개별 ray 유한식 차이 `{0,{0,0,0}}`; 초기 strict `W0>0.007175`는 조건부 유리수 프로그램 검증; 1,604 GL 관측량은 `numerically checked`, 본 소스·구현의 실제 테스트는 `implementation verified`. True continuous six-cell source 전 시간구간 W 부호, 광학/편광 관측량, genuine distinct-author R6/C9, production은 UNRESOLVED/NOT_RUN.

## 원전

- J. Mark Heinzle & Claes Uggla (2006), *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG **23**, 3463–3489, DOI https://doi.org/10.1088/0264-9381/23/10/016.
- Hamed Barzegar, David Fajman & Gernot Heißel (2020), *Isotropization of Slowly Expanding Spacetimes*, PRD **101** 044046, DOI https://doi.org/10.1103/PhysRevD.101.044046.
- Ho Lee, Ernesto Nungesser & Paul Tod (2020), *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen. Relativ. Gravit. **52** 48, DOI https://doi.org/10.1007/s10714-020-02699-7.

위 원전은 Bianchi I Vlasov의 보존과 비등방 동역학 배경이다. 특정 six-cell의 `W0` 하계 및 이번 수치 데이터는 본 연구의 직접 유도이며 문헌의 신기성·우선권을 선언하지 않는다.
