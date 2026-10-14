# REI 이론 인계: signed shear 응답과 초기 등방 복사의 명시적 보정 상계

2026-10-14. BASS 이론 스레드가 실제 REI Codex 작업트리를 읽고 준비한 additive 결과다. Canonical REI state나 진행 중인 driver는 수정하지 않았다. 이 문서는 새로운 재이온화 이력의 실행 결과가 아니다.

## 1. 실제 개발 상태와 고정 모델

2026-10-14 07:38:35 UTC, 즉 16:38:35 KST의 실제 REI HEAD는 `1977423764b51c857c823ebaeff2798c147f56db`, branch `codex/rux-science-delivery-20261014`다. STATE의 AX06은 `COMPLETED / SCOPED_PILOT_PASS / PASS_SCOPED_TWO_PILOTS_NOT_FULL_HISTORY`, AX07·AX08은 `READY`, AX11·AX12는 `PENDING`이었다. Full-history 준비 및 실제 실행은 소유 Codex 세션이 진행한다. 먼저 관찰했던 `0d29446...`와 AX06 진행 중 상태는 과거 snapshot이다. AX07·08을 READY로 만든 주체는 이 스레드가 아니라 완료된 pilot과 그 owner의 심사다.

초기 pilot 중단은 output cap이었다. Codex가 scalar accepted rows는 모두 보존하고 full spectra의 저장 cadence만 바꾸었으며 revised binary `fc9dac5d0af16e159af64ed406cc4c2d2f7918362836546ad15eef5d6f836a46`의 두 pilot을 소비했다. 기존 실패를 지우거나 같은 pilot을 재시작하지 않는다.

사용한 시나리오는 `SCENARIO_LOCK.json` SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`다.
\[
 ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
 \quad s=\dot b,\quad H_\perp=H-s,\quad H_\parallel=H+2s. \tag{REIT.1}
\]
\(\sigma^2=\sigma_{ij}\sigma^{ij}/2=3s^2\), \(a_*=1/21\), \(a_f=1/5\), \(b_*=0\). 시간은 각각의 matched \(\bar z=20\) slice 이후의 gas proper elapsed time이지 absolute cosmic age가 아니다.
\[
 H_F^2=H_0^2(\Omega_r a^{-4}+\Omega_m a^{-3}+\Omega_\Lambda),\quad
 s=qH_F(a_*)(a_*/a)^3,\quad H=\sqrt{H_F^2+s^2}. \tag{REIT.2}
\]
\(q=s_*/H_F(a_*)\)는 고정 case parameter, \(s/H\)는 변화하는 instantaneous shear다. \(q\in\{0,\pm.005,\pm.01\}\). 실제 \(\Omega_m=.315,\Omega_r=.000092,\Omega_\Lambda\simeq.684908\), \(H_0=67.4\) km/s/Mpc다. Source는 동일한 isotropic comoving law, gas·ionization·temperature는 coupled solved outputs다. Source를 \(a\)에 맞추는 것과 서로 다른 배경의 proper time에 맞추는 것을 혼동하지 않는다.

이 배경은 prescribed stress-free EoR family다. Early-time CMB likelihood를 통과한 primordial shear 모델이나 self-consistent radiation-stress solution으로 승격하지 않는다. 원자율·Case-A escape·source·초기조건은 기존 owner가 정한 것을 그대로 둔다.

## 2. 선형 scalar shear 응답이 사라지는 정리

**명제 REIT-S1.** \(q=0\)의 background·photon IC·emissivity·국소 collision law가 rotationally invariant이고, shear 외의 외부 방향 텐서가 없으며, 동일 coordinate의 해가 \(q\)에 대해 충분히 미분 가능하고 유일하다고 하자. 이때 local scalar abundance·gas temperature의 \(q=0\) 선형 응답은 0이다.

증명은 두 방식으로 확인할 수 있다. 첫째, trace-free shear 방향 \(S_{ij}=3z_iz_j-h_{ij}\)에 대한 scalar의 선형 functional은 isotropic background에서 \(A h^{ij}S_{ij}\)여야 한다. \(h^{ij}S_{ij}=0\)이므로 응답이 없다. 실제 xTensor 계산은 이 contraction과 \(\sigma^2=3s^2\)를 정확히 확인했다.

둘째, homogeneous Boltzmann 식의 anisotropic redshift는 \(-\sigma_{ij}n^in^j E\partial_Ef\)이다. Isotropic \(f_0\)에 대한 일차 forcing은 순수 \(\ell=2\)다. 회전 불변 linear collision operator는 이 forcing을 \(\ell=0\)로 섞지 않는다. Direction drift는 angularly constant \(f_0\)에 작용하면 0이다. Scalar chemical/photoheating rate가 monopole을 읽고 homogeneous scalar 초기변화가 없다면 그 일차 변화도 0이다. Primary \(H-H_F\)는 이미 \(O(q^2)\)이다.

따라서 분석적 확장을 할 수 있는 구간에서
\[
 X(q,\xi)=X_0(\xi)+A_2(\xi)q^2+A_3(\xi)q^3+O(q^4),
 \quad \xi=a\;\hbox{또는 matched proper time}. \tag{REIT.3}
\]
이는 **정확한 \(X(q)=X(-q)\) 대칭이 아니다**. \(\operatorname{tr}\sigma^3=6s^3\)인 회전 scalar가 허용된다. Uniaxial eigenvalue 집합 \((-s,-s,2s)\)와 \((s,s,-2s)\)는 일반적으로 회전으로 연결되지 않는다. Photon direction 반전의 reflection parity와 shear sign 반전은 다르다.

Anisotropic IC·source, 외부 magnetic tensor, tilt, finite pointing detector, 비등방 closure, threshold/domain crossing의 nonsmooth branch는 이 정리의 가정을 다시 검사해야 하는 경우다. Finite-grid angular leakage도 가능하므로 이 정리를 이용해 출력을 강제로 대칭화하거나 선형항을 지우면 안 된다. 특히 BASS FA-03의 finite-cap 관측량은 여기의 scalar 가정을 만족하지 않는다.

## 3. 기존 다섯 case를 그대로 사용하는 검증식

동일 좌표에서
\[
 E(q)=\frac{X(q)+X(-q)}2-X(0),\qquad
 O(q)=\frac{X(q)-X(-q)}2 \tag{REIT.4}
\]
를 만든다. 해결된 leading response에서는 \(E(q)/E(q/2)\to4\), \(O(q)/O(q/2)\to8\)가 예상된다. 그러나 수치 floor 아래에서는 이 비를 만들지 않는다.

다섯 case로 선형 leakage·quadratic·cubic coefficient를 구분할 수 있다.
\[
 \widehat A_1=\frac{8O(q/2)-O(q)}{3q},\quad
 \widehat A_2=\frac{16E(q/2)-E(q)}{3q^2},\quad
 \widehat A_3=\frac{4[O(q)-2O(q/2)]}{3q^3}. \tag{REIT.5}
\]
일반 expansion에서 첫 식은 cubic를 제거하고 \(A_1+O(q^4)\), 둘째는 quartic을 제거하고 \(A_2+O(q^4)\), 셋째는 linear를 제거하고 \(A_3+O(q^2)\)다. `code/rei_theory_checks.py:signed_coefficients`가 이 순수 대수 연산을 제공한다. Interpolation, history matching, uncertainty propagation은 하지 않으며 데이터의 과학적 통과를 판정하지 않는다.

기존 absolute fraction floor \(10^{-7}\), temperature floor .01 K, baryon-scaled species floor, paired numerical target는 보존한다. Divided coefficient의 오차는 \(q^{-1},q^{-2},q^{-3}\)로 증폭되므로 먼저 원래 \(E,O\)를 uncertainty와 비교해야 한다. Null 또는 unresolved 결과가 정상적인 결론일 수 있다. Source/IC sensitivity는 numerical convergence와 다른 오차 범주다.

## 4. Proper-time와 scale-factor 비교의 변환

\[
 \tau(a,q)=\int_{a_*}^{a}\frac{d\ln a'}{H(a',q)},\quad
 r(a)=\frac{H_F(a_*)}{H_F(a)}(a_*/a)^3.
\]
같은 \(a\)에서
\[
 \tau(a,q)=\tau_0(a)-\frac{q^2}{2}
 \int_{a_*}^a\frac{r(a')^2}{H_F(a')}d\ln a'+O(q^4). \tag{REIT.6}
\]
즉 clock 차이는 \(O(q^2)\)이며 scalar의 선형 소거와 모순되지 않는다. 처음 비영인 차수에서
\[
 \delta X|_{\tau}=\delta X|_a-\dot X_0\,\delta\tau(a). \tag{REIT.7}
\]
이 식은 \(\tau_q(a_q)=\tau_0(a_0)\)의 역함수 전개로 얻는다. 실제 history 비교는 지정한 하나의 coordinate에서 수행하고 candidate·reference의 다른 coordinate도 보존한다. Transverse milestone \(X_0(\tau_*)=X_*\), \(\dot X_0\ne0\)이면 \(\delta\tau_*=-\delta X|_\tau/\dot X_0\). 평탄한 crossing이나 미도달 milestone은 이 나눗셈을 쓰지 않고 censored/ill-conditioned로 보고한다. Temperature plot은 시간순 경로를 그리며 온도로 재정렬하지 않는다.

## 5. 초기 등방 복사의 exact stress와 비대칭성

\(b_*=0\)에서 등방인 collisionless massless distribution을 고려한다. 초기 방향 cosine \(\mu_0\)에 대해
\[
 D(b,\mu_0)=\sqrt{e^{2b}(1-\mu_0^2)+e^{-4b}\mu_0^2},\quad
 E/E_*=a_*/a\,D. \tag{REIT.8}
\]
\(U_{\rm iso}\propto a^{-4}\)로 놓으면
\[
 \Phi(b)=\frac{U}{U_{\rm iso}}=\frac12\int_{-1}^1D\,d\mu_0,
\quad
 \frac{\Delta P}{U_{\rm iso}}=
 \frac12\int_{-1}^1\frac{e^{-4b}\mu_0^2-\tfrac12e^{2b}(1-\mu_0^2)}{D}\,d\mu_0
 =-\frac12\Phi'(b), \tag{REIT.9}
\]
\(\Delta P=P_\parallel-P_\perp\). 이는 photon momentum 변환과 양의 초기 angular measure로부터 나온다. Repo의 local-direction temperature 식과 동치이지만 angle Jacobian 없이 초기 방향과 현재 방향을 바꾸어 쓰면 안 된다. Trace-free shear work는 \(\sigma:\pi=2s\Delta P\), 따라서 \(\dot U+4HU+2s\Delta P=0\)가 정확히 성립한다.

실제 Wolfram 계산은
\[
 \Phi=1+\tfrac85b^2-\tfrac{16}{21}b^3+\tfrac8{35}b^4+O(b^5),\quad
 \Delta P/U_{\rm iso}=-\tfrac85b+\tfrac87b^2-\tfrac{16}{35}b^3+O(b^4) \tag{REIT.10}
\]
와 \(\Phi'+2\Delta P/U_{\rm iso}=0\)를 검산했다. \(b^3\)는 REIT-S1에서 허용한 scalar odd response의 명시적 예다.

## 6. 화학 이력 없이 닫히는 analytic feedback diagnostic 상계

**명제 REIT-R1.** 위 fixed prescribed background, \(a\in[1/21,1/5]\), \(|q|\le .01\), 처음 등방인 전체 effective \(\Omega_r\) massless fluid에 대해, 아래에 정의한 omitted-stress first-variation functional은
\[
 \sup_a\frac{|\delta s_{\rm rad}(a)|}{H(a)}<2.61\times10^{-5},\qquad
 \sup_a\frac{U_{\rm rad}-U_{\rm iso}}{E_{\rm bg}}<8.68\times10^{-7} \tag{REIT.11}
\]
를 만족한다. 첫 상계는 실제 REI lock의 \(10^{-4}\) diagnostic ceiling보다 작다. Ionizing radiation·gas thermal correction은 포함하지 않는다.

증명. \(H\ge H_F\ge H_0\sqrt{\Omega_m}a^{-3/2}\)이고
\[
 |b(a)|\le k_b[1-(a_*/a)^{3/2}],\quad
 k_b=\frac23|q|\sqrt{1+\frac{\Omega_r}{\Omega_m a_*}
                       +\frac{\Omega_\Lambda a_*^3}{\Omega_m}}. \tag{REIT.12}
\]
\(\Omega_\Lambda\le.684909\)인 보수적 유리수 상한을 사용해 binary64 반올림도 포함하면 \(k_b<.006688\), \(B:=\sup|b|<.005911\), \(4e^{2B}<4.048\)이다.

\(D^2=\sum_iw_i e^{\lambda_i b}\), \(w_i\ge0\), \(\lambda_i\in\{2,-4\}\)이므로
\[
 D''/D=\tfrac12\langle\lambda^2\rangle_b-\tfrac14\langle\lambda\rangle_b^2,
 \qquad 0\le D''\le8D\le8e^{2B}.
\]
\(\Phi'(0)=0\)를 이용해 적분하면
\[
 |\Delta P|/U_{\rm iso}\le4e^{2B}|b|,\quad
 0\le\Phi-1\le4e^{2B}b^2. \tag{REIT.13}
\]
Repo의 diagnostic functional은
\[
 \delta s_{\rm rad}(a)=a^{-3}\int_{t_*}^{t}
 a'^3\frac{8\pi G}{3c^2}\Delta P_{\rm rad}(t')dt'. \tag{REIT.14}
\]
\(U_{\rm iso}=3c^2H_0^2\Omega_r a^{-4}/(8\pi G)\)를 대입하고 위 \(H\) 하한으로 적분하면, \(r=a/a_*\),
\[
 \frac{|\delta s_{\rm rad}|}{H}
 \le\frac{\Omega_r}{\Omega_m a_*}(4e^{2B})k_b f(r),\quad
 f(r)=2/r-3/r^{3/2}+r^{-5/2}. \tag{REIT.15}
\]
\(r\in[1,21/5]\)에서 도함수의 양의 내부 극대는
\(r_{\rm pk}=[(5+\sqrt{105})/8]^2\)이고, \(f(r_{\rm pk})<.1571\). 도함수의 다른 양의 root는 \(r=1\) 경계이며 이후 큰 \(r\)에서 감소하므로 최대 판정은 표본검색이 아니다. 실제 exact ratio \(\Omega_r/(\Omega_m a_*)=23/3750\)와 유리수 상계로
\[
 \frac{23}{3750}\frac{506}{125}\frac{6688}{10^6}\frac{1571}{10^4}
 =\frac{1910604641}{73242187500000}
 =2.60861220317866\ldots\times10^{-5}<2.61\times10^{-5}.
\]
또한 \(E_{\rm bg}=3c^2H_F^2/(8\pi G)\ge3c^2H_0^2\Omega_m a^{-3}/(8\pi G)\)이므로
\[
 \frac{U-U_{\rm iso}}{E_{\rm bg}}
 \le\frac{23}{3750}\frac{506}{125}\left(\frac{5911}{10^6}\right)^2
 =\frac{203315400299}{234375000000000000}<8.68\times10^{-7}. \tag{REIT.16}
\]
모든 finite rational 비교와 극점 도함수의 0은 실제 Wolfram에서 검산되었다.

**정확한 적용 범위.** 이는 prescribed path 위의 perturbative diagnostic functional 자체에 대한 analytic bound다. Self-consistent Einstein–Boltzmann 해와의 전체 오차, abundance response 오차, Compton temperature approximation 오차, physical massive-neutrino stress의 모델 오차를 bound한 것이 아니다. Whole effective \(\Omega_r\)를 massless free-streaming reference로 쓰는 것은 기존 선택 모델의 보수적 진단이며 원자율로 바꾸어 해석하지 않는다. AX03의 ionizing quadrupole와 thermal/extra-energy 의무는 실제 coupled output으로 별도 평가한다.

## 7. 독립적인 경량 수치 판별과 소비 지점

`rei_theory_checks.py`는 chemistry 없이 prescribed \(b\), REIT.14의 적분, proper clock을 DOP853로 적분하고 angular GL64와 refinement GL96을 비교했다. \(q=+.01,-.01\)의 sampled max \(|\delta s|/H\)는 각각 \(1.01444\times10^{-5},1.02105\times10^{-5}\), extra radiation energy ratio는 약 \(9.67\times10^{-8}\)이다. 둘 다 analytic 상계보다 작다. 모든 저장 column의 refinement 최대차는 \(3.95\times10^{-12}\), 10개 판별 기준이 충족되었다. Gaussian quadrature의 미소 q=0 잔차 \(2.49\times10^{-18}\)는 정확히 0이라는 이론값을 대체하지 않는다.

별도 full-history나 atomic solve는 실행하지 않았다. 첫 JSON 직렬화에서 numpy boolean 타입 오류가 발생했으며 raw failure를 보존한 뒤 JSON 경계에서 bool 변환만 수정했다. 이는 수치·물리 실패가 아니다.

이제 준비된 작업은 AX03 **초기 등방 effective-radiation diagnostic 소비**, AX11 **다섯 case signed-response 분석 구현**, 그리고 **ZBAR/PROPER_TIME 비교 계약**이다. 이 자료의 소비는 AX07·08 실행을 새로 막는 선행조건이 아니다. AX11 과학적 완료에는 실제 full histories, refinement와 uncertainty 비교가 여전히 필요하다.

## 원전과 근거

Fleury, Pitrou & Uzan, arXiv:1410.8473, §§II·IV의 Bianchi I shear와 conserved momentum을 사용하되, 그 문헌의 conformal shear 및 \(\sigma_{ij}\sigma^{ij}\) convention을 본문의 proper-time half-contraction convention으로 변환했다. Einstein difference equation은 \(\dot s+3Hs=(8\pi G/3c^2)\Delta P\)가 된다. 원전 확인은 SciSpace 검색과 Exa 본문 읽기로 수행했다. REIT-S1·R1과 explicit rational bounds는 본문의 직접 유도이며 문헌상의 선행성/최초성을 주장하지 않는다.
