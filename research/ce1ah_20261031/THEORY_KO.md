# BASS CE1-AH | 원본 six-cell Einstein–Vlasov의 constraint-preserving 초기전단 tangent response

2026-10-31 KST. 기준: `cosmosapjw-quantum/bass`, immutable Draft PR286 `4d6a5d9c391bbd5aac1a885ff72b4f33f027e28a`. Parent CI/PR286 원본 파일은 수정하지 않는다.

## 1. 목적, 모델, 원전

질문: 정확히 같은 무질량, 충돌 없는 reflection-even 여섯 개 양의 연속 각도 cell 분포를 고정했을 때, 초기 traceless shear 두 방향에 대한 진짜 **Einstein-응답을 포함한** photon fractional multipoles `C2`, `C4`, shear-work `W`, photon energy `E`의 tangent map은 무엇인가?

계량은 `ds²=-c²dt²+Σ_i a_i(t)² (dx^i)²`, signature (-,+,+,+), Λ=0, 대각 Bianchi I. 시간 `u=t/Tstar ∈[0,2/25]`, `ell_i=ln a_i`, `h_i=ell_i'`, `H=Σ h_i/3`, `sigma_i=h_i-H`. 모든 `E,P,R`는 원 BASS Einstein-scale dimensionless variables. 실제 CMB temperature나 polarization은 정의하지 않는다. `c`는 SI 단위로 환산할 때 보존하며 모형에서 새로운 natural-unit 설정을 도입하지 않는다.

Source SHA256: `022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035` (128 original `<f8` input bytes; `MU`, `PHI`, `CELL_E`, `SHEAR`). 원래 geometry h target `1e-5`는 변경하지 않는다. 원래 source 내부 8 reflections는 positive-octant angular cells의 reflection-even 대칭으로 반영된다.

Background literature (scope only, not proof of specific CE1-AH numbers):
- Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, Class. Quantum Grav. 23 (2006) 3463–3489, DOI `10.1088/0264-9381/23/10/016`, arXiv:gr-qc/0512031.
- Lee, Nungesser & Tod, *On the future of solutions to the massless Einstein–Vlasov system in a Bianchi I cosmology*, Gen. Relativ. Gravit. 52 (2020) 48, DOI `10.1007/s10714-020-02699-7`, arXiv:1911.04937.
- Barzegar, Fajman & Heißel, *Isotropization of Slowly Expanding Spacetimes*, Phys. Rev. D 101 (2020) 044046, DOI `10.1103/PhysRevD.101.044046`.

위 문헌의 Bianchi-I 기본 구조와 기존 CE1AF의 Liouville moments를 재사용한다. 다음 유도는 **현재 프로젝트의 선택한 model-specific tangent formulation**이며 일반 선형응답 이론의 신규성 주장은 하지 않는다.

## 2. 기본 계와 exact angular Jacobian

보존 공변 방향 `n_i`, 원본 양의 분포 `U0(n)`에 대해

```
V=exp(-Σ ell_i), Q=Σ n_i² exp(-2ell_i), r=sqrt(Q), x_i=n_i² exp(-2ell_i)/Q
E=V∫U0 r dΩ, P_i=V∫U0 r x_i dΩ, R_ik=V∫U0 r x_i x_k dΩ.
```

`Σ_i P_i=E`, `Σ_k R_ik=P_i`, `R ≽ 0`. 본래 6D Einstein–Vlasov IVP는

\[
\ell_i'=h_i,\qquad h_i'=-\theta h_i+P_i,\quad\theta=\sum_jh_j,\quad
3H^2=E+\tfrac12\sum_i\sigma_i^2.
\]

연속 angular integrals를 직접 미분하면

\[
\boxed{\partial_{\ell_k}E=-E-P_k,\qquad
\partial_{\ell_k}P_i=-P_i-2\delta_{ik}P_i+R_{ik}.}\tag{1}
\]

이는 pressure response가 실제 4차 모멘트 `R`에 의존함을 보인다. `P_i`만으로 닫힌 perfect-fluid Ansatz를 도입하지 않는다.

## 3. 두 개의 constraint-preserving tangent IVP

`a∈{A,B}`에서 `dσ_A=(1,-1,0)`, `dσ_B=(1,1,-2)`를 정의하고

\[
\sigma_i(0;\epsilon_a)=\sigma_i^{(0)}+\epsilon_a d\sigma_{a,i},\qquad
E(0;\epsilon_a)=E_0,\quad\ell_i(0;\epsilon_a)=0,
\]

\[
H(0;\epsilon_a)=\sqrt{\frac{E_0+\frac12\sum_i\sigma_i(0;\epsilon_a)^2}{3}},\quad
h_i(0;\epsilon_a)=H(0;\epsilon_a)+\sigma_i(0;\epsilon_a).
\]

따라서 **꼭 필요한** 초기 tangent constraint는

\[
\boxed{\delta\ell_i(0)=0,\quad
\delta H(0)=\frac{\sum_i\sigma_i(0)d\sigma_i}{6H_0},\quad
\delta h_i(0)=d\sigma_i+\delta H(0).}\tag{2}
\]

여기서 `δ`는 `∂/∂ε_a |_{ε=0}`이다. `δH=(σ·dσ)/(3H)`는 두 배의 오류이며 허용하지 않는다.

(1)을 이용한 tangent system은

\[
\boxed{(\delta\ell_i)'=\delta h_i,\quad
(\delta h_i)'=-\theta\delta h_i-h_i\sum_j\delta h_j+
\sum_k(-P_i-2\delta_{ik}P_i+R_{ik})\delta\ell_k.}\tag{3}
\]

`C=Σ_{i<j}h_ih_j-E`는 `C'=-2θC`, 변분에 대해서는

\[
(\delta C)'=-2\theta\delta C-2\delta\theta C,\qquad
\delta C=\sum_i(\theta-h_i)\delta h_i-\delta E,
\]

이므로 초기 `C(0)=δC(0)=0`이 정확히 보존된다. 이 계약이 **고정 기하의 순간 미분**과 다른 점이다.

## 4. 측정가능량: normalized harmonic and shear-work response

현재 물리 방향의 제곱 `x_i`로 Condon–Shortley real spherical harmonics `Y20,Y22,Y40,Y42,Y44`를 다항식으로 계산한다. 특히

\[
Y_{20}=\sqrt{\frac5{16\pi}}(3x_z-1),\quad
\Re Y_{22}=\sqrt{\frac{15}{32\pi}}(x_x-x_y),
\]
\[
Y_{40}=\frac3{16\sqrt\pi}(35x_z^2-30x_z+3),\quad
\Re Y_{42}=\frac38\sqrt{\frac5{2\pi}}(7x_z-1)(x_x-x_y),
\]
\[
\Re Y_{44}=\frac3{16}\sqrt{\frac{35}{2\pi}}(x_x^2-6x_xx_y+x_y^2).
\]

정규화 계수 `alpha_lm=4π ⟨Y_lm⟩_ω` (`ω=V U0 r dΩ`, `⟨·⟩_ω=∫ω·/E`)의 변분은

\[
\boxed{\delta\alpha_{lm}=4\pi\bigl[\langle\delta Y_{lm}\rangle_\omega
-\mathrm{Cov}_\omega(Y_{lm},\sum_kx_k\delta\ell_k)\bigr],}\tag{4}
\]

`δx_i=2x_i(Σ_kx_kδell_k−δell_i)`. Common spatial-scale 변분에 대해 `(∂_ell1+∂_ell2+∂_ell3)alpha_lm=0`이 정확하다. 이 관계와 SciPy `sph_harm_y`에 대한 별도 검산을 시행한다.

\[
C_2=\frac{\alpha_{20}^2+2\alpha_{22}^2}{5},\quad
C_4=\frac{\alpha_{40}^2+2\alpha_{42}^2+2\alpha_{44}^2}{9},\quad
W=\sum_i\sigma_i(P_i-E/3),\qquad q=W/E.
\]

\[
\delta W=\sum_i\delta\sigma_i\Pi_i+\sigma_i(\delta P_i-\delta E/3),\quad
\delta q=(\delta W-q\delta E)/E.
\]

원본 radiation-volume compensation `F(u)=E(u)e^{4\bar\ell(u)}/E(0)`은 source가 고정되어 `δE(0)=0`이므로

\[
\boxed{\delta\ln F=\frac{\delta E}{E}+\frac43\sum_i\delta\ell_i
=-\int_0^u\delta q(v)\,dv.}\tag{5}
\]

## 5. Computational form, evidence and limits

- Code: `source/ce1ah_tangent.py`, baseline 6D + 두 모드별 6D의 **18D** tangent ODE, SciPy DOP853, original GL6/8/16 ray weights, 401 epochs, `rtol=3e-12`, `atol=3e-14` (코딩 수치 선택; original h error target은 변경하지 않음).
- 별도로 초기 전단 ±1e-4 방향의 **진짜 6D fully nonlinear Einstein–Vlasov IVP**를 GL6/8에 대해 통합하여 중앙차분으로 tangent를 검증했다. ± perturbation은 source를 바꾸지 않지만 **원본 initial shear 자체는 perturbation**되는 validation family다. 이 family를 원래 여섯 cell의 고유 baseline 관측값이라고 부르지 않는다.
- Derivation is exact **at the continuum moment level**; GL6/8/16 numerical values are not certified enclosures of angular-continuum. No blackbody spectrum or statistical CMB multipoles/lensing inference.
- Changed scope is CE1AH one bounded science unit. Upper BASS DAG **9/15**, 21 edges, CE1 PARTIAL, scoped R/C 18/20, new upper completed nodes **0**. R6/C9 genuine distinct-author NOT_RUN, production/merge HOLD, no auto-next.
