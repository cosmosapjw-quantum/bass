# S6: 유한 d angular 오차, rank1 certificate, spectral 잔차와 cohort 합성

작성일: 2026-10-19. 물리 범위는 S3와 같다. Non-tilted axisymmetric Bianchi I,
signature `(-,+,+,+)`, `a_perp=a e^{-b}`, `a_parallel=a e^{2b}`, `s=dot b`,
`Sigma=sqrt(3)|s|/H`. 기호 `d, z=mu^2, A, B, R, D, F, G, A=G/F, M_l`은
[S3_THEORY_KO.md](S3_THEORY_KO.md)를 그대로 따른다. 모든 식은 무차원이다.
새로 선언된 locally isotropic source의 birth weights만 다루고 그 weights는
이후 수송에서 고정한다. 기존 광자장과 물리적 anisotropic source는 대상이 아니다.

## 1. 유한 d 오차의 정확한 moment 분해

\(K(d,\mu)=D(d,\mu)-\mathcal A_{\rm iso}(d)R(d,\mu)\)라 하자.
\(\langle K\rangle_{\rm iso}=G_{\rm iso}-\mathcal A_{\rm iso}F_{\rm iso}=0\)이다.
양의 정규화 rule \(\alpha\)에 대해

\[
\mathcal A_\alpha(d)-\mathcal A_{\rm iso}(d)
=\frac{\langle K\rangle_\alpha}{F_\alpha(d)}
=\frac{1}{F_\alpha(d)}\sum_{\ell\ge2,\ \ell\ \rm even}k_\ell(d)\,M_\ell^\alpha,
\qquad k_\ell=\tfrac{2\ell+1}{2}\int_{-1}^1K P_\ell\,d\mu . \tag{S6.1}
\]

이 식은 근사 없이 성립한다. \(K\)가 \(\mu\)에 짝수이므로 홀수 \(\ell\)은 정확히 0이다.
\(k_\ell(d)\)는 rule과 무관한 물리 kernel이고 \(M_\ell^\alpha\)는 rule만의 성질이다.
따라서 moment 제약은 특정 \(M_\ell\)을 0으로 만들고, angular refinement는 모든
고차 \(M_\ell\)을 작게 만든다. 두 효과를 같은 식에서 분리해 측정할 수 있다.
소-d 극한에서 \(k_2=1-\tfrac{10}{7}d+O(d^2)\), \(k_4=\tfrac{36}{35}d+O(d^2)\)로
S3의 (S3.4)를 재현한다.

## 2. 분기점과 Bernstein ellipse

\(R^2=e^{2d}+(e^{-4d}-e^{2d})\mu^2\)는 \(\mu_s^2=1/(1-e^{-6d})\)에서 0이다.
\(d>0\)이면 \(\mu_s\)는 실수 \(>1\), \(d<0\)이면 순허수다. 두 경우 모두
\(\mu_s\)를 지나는 ellipse \(E_\rho\)(초점 \(\pm1\))의 parameter는

\[
\boxed{\rho(d)=\sqrt{\coth\!\big(\tfrac32|d|\big)}} \tag{S6.2}
\]

이다. 예를 들어 \(\rho(0.2)=1.85277\), \(\rho(0.05)=3.6549\)다.
\(K\)는 \(E_\rho\) 내부에서 해석적이므로 \(|k_\ell|\)은 \(\rho(d)^{-\ell}\)로 감소한다.
저장 계수에서 \(|k_\ell(0.2)|\rho^\ell\)은 \(\ell=6\)–\(78\)에서 1.45–1.28로
거의 일정했다.

**엄밀한 계수 상한.** \(1<\rho'<\rho(d)\), \(a=(\rho+\rho^{-1})/2\)라 하자. 초점이 같은
ellipse 사이의 거리는 elliptic 좌표에서 \(|d\mu|\ge\sinh\xi\,d\xi\)이므로
\(a_d-a'\) 이상이다. 따라서 \(E_{\rho'}\) 위에서
\(|R^2|\ge|c|(a_d-a')^2\), \(c=e^{-4d}-e^{2d}\), \(|\mu|\le a'\)이고
\(|K|\le M\)을 닫힌 식으로 얻는다. Chebyshev 계수 \(|c_k|\le2M\rho'^{-k}\)와
\(\int|P_n|\le2/\sqrt{2n+1}\)로

\[
|k_n|\le\frac{2M}{1-\rho'^{-1}}\sqrt{2n+1}\,\rho'^{-n}. \tag{S6.3}
\]

\(\rho'\)를 19개 후보 중 최적으로 골라 \(\sum_{n>L}|k_n|\)을 상한한다(`tail_bound`).
\(L=100\)에서 저장 grid의 최대 tail은 \(1.005\times10^{-22}\)이었다.
계수는 30자리 비구간 계산이며 40자리와의 차이는 \(10^{-28}\) 미만이었다.
상한에는 별도 산술 여유 \(10^{-25}\)를 더한다.

## 3. 제약만으로 보장되는 오차와 필요한 차수

\(M_2=\dots=M_{2m}=0\)이고 나머지 \(|M_\ell|\le1\)만 안다면

\[
|\mathcal A_\alpha-\mathcal A_{\rm iso}|\le
\frac{\sum_{\ell>2m}|k_\ell(d)|+{\rm tail}}{\min_\mu R},\qquad
\min_\mu R=\min(e^{d},e^{-2d}). \tag{S6.4}
\]

이 보장은 차수 하나를 추가할 때마다 대략 \(\rho(d)^2\)배만 줄어든다.

| d | ρ(d) | P2만 | P2/P4 | P2..P6 | P2..P8 | 1e-6에 필요한 m |
|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | 8.165 | 1.05e-2 | 1.43e-4 | 2.06e-6 | 3.01e-8 | 4 |
| 0.05 | 3.655 | 5.64e-2 | 3.86e-3 | 2.77e-4 | 2.03e-5 | 6 |
| 0.1 | 2.592 | 1.22e-1 | 1.67e-2 | 2.40e-3 | 3.49e-4 | 8 |
| 0.2 | 1.853 | 2.76e-1 | 7.47e-2 | 2.11e-2 | 6.02e-3 | 12 |

즉 d=0.2에서 moment 제약만으로 \(10^{-6}\)를 보장하려면 P2부터 P24까지 0이어야
한다. 이것은 양의 해를 가지려면 많은 서로 다른 z 지지가 필요하다는 뜻이다.
P2/P4만으로 continuum 정확도를 승인하지 않는 정량적 근거다.

## 4. Angular refinement의 수렴률

S3의 `lrs_rule(b,n)`은 GL nodes \(m_i\)를 \(\mu=me^{-2b}/R(b,m)\)로 보낸다.
\(d\mu/dm=1/R(b,m)^3\)이므로 prior \(q_i\propto w_i/R(b,m_i)^3\)는 균일 측도의
정확한 pushforward다. 또한 cocycle

\[
R\big(d,\mu(m)\big)\,R(b,m)=R(b+d,m) \tag{S6.5}
\]

이 성립한다. 따라서 \(m\) 공간의 피적분함수 특이점은 \(R(b,\cdot)\)와
\(R(b+d,\cdot)\)의 영점뿐이고, GL n점 오차는

\[
|\mathcal A_q-\mathcal A_{\rm iso}|\sim C\,\rho_*^{-2n},\qquad
\rho_*=\min\{\rho(b),\rho(b+d)\} \tag{S6.6}
\]

의 점근 거동을 갖는다. KL tilt \(\exp(\lambda_2P_2+\lambda_4P_4)\)는 같은
특이점만 가지므로 P2/P24 rule도 같은 비율을 갖는다. 이는 점근식이다. 저장
캠페인에서 사전 gate(n≥16, 비율 0.7–1.4)는 \(2n\ln\rho_*<6.4\)인 큰 b에서
실패했고, \(2n\ln\rho_*\ge10\) 기준은 그 데이터를 본 뒤 정했다. 그래서 겹치지 않는
grid에서 별도로 검사했다([S6_RESULTS_KO.md](S6_RESULTS_KO.md) 참조).

필요 ray 수는 \(n\gtrsim\ln(C/\varepsilon)/(2\ln\rho_*)\)이며 \(|b+d|\to\infty\)에서
\(\ln\rho_*\approx e^{-3|b+d|}\)이므로 지수적으로 증가한다. C=1, ε=1e-6 기준:

| b | d | ρ* | 필요 n | 점근 시작 n(=5/ln ρ*) |
|---:|---:|---:|---:|---:|
| 0 | 0.2 | 1.853 | 11 | 8 |
| 0.3 | 0.2 | 1.255 | 30 | 22 |
| 0.6 | 0.2 | 1.095 | 76 | 55 |
| 1.0 | 0.2 | 1.028 | 253 | 183 |
| 1.5 | 0.2 | 1.006 | 1133 | 820 |

현재 native는 n_mu=8/16/32만 지원하므로 \(|b|\gtrsim0.6\)의 누적 비등방에서는
angular refinement가 부족하다는 것이 이 기준의 예측이다. C는 rule별 상수이며
이 표는 수렴률 예측이지 엄밀 상한이 아니다. 엄밀 판정은 (S6.1)+(S6.3)의
a posteriori certificate로 한다.

## 5. Exact rank1 certificate

서로 다른 z가 두 개일 때 양의 P2/P4 해는
\(z_1<1/3<z_2\), \(15z_1z_2-5(z_1+z_2)+3=0\)일 때만 존재한다(S3 정리, m=2).
입력 certificate는 정수 계수 이차식 \(c_2z^2+c_1z+c_0\)이다.
\(s=-c_1/c_2\), \(p=c_0/c_2\)에 대해 다음을 모두 `Fraction`으로 정확히 검사한다.

1. 판별식 \(s^2-4p>0\).
2. 두 근이 [0,1]: \(s\ge0,\ p\ge0,\ 2-s\ge0,\ 1-s+p\ge0\).
3. 엄격한 bracketing: \(1/9-s/3+p<0\).
4. 호환성: \(15p-5s+3=0\).
5. Binding: 각 binary64 ray의 \(\mu^2\)(정확한 dyadic 유리수)에서
   \([\mu^2-2^{-48},\mu^2+2^{-48}]\)가 vertex \(s/2\)를 포함하지 않고 부호가
   바뀌면 그 구간의 유일한 근에 배정한다. 정확히 근이면 그대로 배정한다.

rank1에서는 group 총량이 moment로 유일하게 정해지고 KL 최소해는 group 안의
prior 비를 유지한다. 최종 binary64 weights는 기존 `3e-15` moment gate,
정규화 `5e-16`, 양성, parity 검사를 그대로 통과해야 한다.
GL4는 \(35z^2-30z+3\), \(z=(0,3/5)\)는 \(5z^2-3z\)가 certificate다.
Native angular grid는 n_mu=8/16/32만 허용하고 단조 사상 후에도 서로 다른 z가
n/2≥4개이므로 native 경로에서는 rank1이 생기지 않는다. 그래서 이 경로는
Python 연구 경로로 둔다.

## 6. Spectral 잔차 5.369926725506957e-12의 원인

고정 owner에서 `AxbiSource::new`는 각 source cell의 photon/energy 적분을
composite Simpson(n=32)으로, `CovariantTransport::source_moments`는 같은 cell과
bin 조각을 GL8로 계산한다. Native deposition은 cell마다 photon 수를
\(\mathrm{pf}_s\)로 맞추고 energy는 GL8 비 \(u_{\rm GL8}/n_{\rm GL8}\)로 넣는다.
Probe의 비교량은

\[
\frac{\sum_s\mathrm{pf}_s\,u^{\rm GL8}_s/n^{\rm GL8}_s}
     {\sum_s\mathrm{pf}_s\,u^{\rm S32}_s/n^{\rm S32}_s}-1 .
\]

40자리 기준값에 대해 GL8 cell mean의 오차는 \(10^{-16}\) 이하이고, Simpson 기준은
\(-5.3697\times10^{-12}\)이다. 따라서 이 잔차는 native deposition 오차가 아니라
**비교 기준인 Simpson cell mean의 절단 오차**다. Simpson 오차는 \(h^4\)이므로
cells_per_segment를 두 배로 하면 약 16배 줄어든다. Bin 조각의 GL8 합은 cell
전체 GL8과 반올림 수준에서 같으므로 bin 수와 angular rule에 무관하다.
최댓값 5.369926725506957e-12와 다수값 5.369704680902032e-12의 차이는
비율의 1 ulp(2.22e-16)다.

## 7. Source-age 합성과 결합 feedback

출생 u의 cohort가 출생 에너지 증분 w와 고정 rule을 가지면

\[
U(x)=\sum_k w_ke^{-4(x-u_k)}F_{\alpha_k}(d_k),\quad
\Delta P(x)=\sum_k w_ke^{-4(x-u_k)}G_{\alpha_k}(d_k),\quad
\frac{dU}{dx}+4U+2b'(x)\Delta P=0
\]

이 출생 사이에서 cohort마다 정확히 성립한다(\(F'=-2G\)). 연속 출생 적분의 오차는
출생시간 quadrature 항과 angular 항으로 나뉜다. Angular 항은 (S6.1)의 cohort
가중합이다.

\[
\delta\Delta P(x)=\sum_k w_ke^{-4(x-u_k)}\sum_{\ell\ge2}g_\ell(d_k)M_\ell^{(k)} .
\]

여기서 \(g_\ell\)은 D의 Legendre 계수다. S3 선도식
\(\tfrac{36}{35}\sum wM_4d\)는 유한 d에서 정량적으로 부족할 수 있다.

**결합 방정식(유도만, 실행 안 함).** \(V=a^3\), \(\beta=(-b,-b,2b)\)에서 trace-free
Einstein 식 \(\partial_t(V\dot\beta_i)=8\pi G V\pi^i{}_i/c^2\)와
\(\pi^3{}_3=P_\parallel-\bar P=\tfrac23\Delta P\)로

\[
\dot s+3Hs=\frac{8\pi G}{3c^2}\,\Delta P_{\rm tot}. \tag{S6.7}
\]

\(\Delta P>0\)이면 s가 커지고, 다음 시점의 d가 증가해 \(\mathcal A'<0\)으로
ΔP가 줄어드는 음의 feedback이다. 고정 배경에서 선형화하면 angular 오차가 주는
shear 오차는 \(\delta s(x)=\int^x e^{-3(x-x')}\tfrac{8\pi G}{3c^2H}\delta\Delta P(x')dx'\)이다.
이 계수와 부호는 고정 owner `axbi_background.rs`의 `omitted_feedback`
(\(k=8\pi G/(3c^2)\), \(a^3\delta s=\int k\,a^3\Delta P\,dt\))와 일치하고, owner의
`rates()`는 \(H=\mathrm{hypot}(H_{\rm FLRW},s)\)를 쓴다(2026-10-19 원문 대조).
Owner의 이 함수는 배경을 바꾸지 않는 섭동 진단이며 결합 진화가 아니다. 결합 실행은 [evidence_s6/COUPLED_FEEDBACK_CONTRACT.json](evidence_s6/COUPLED_FEEDBACK_CONTRACT.json)의
별도 의무로 남긴다.

## 8. 근거 상태

- `derived`: (S6.1)–(S6.7), rank1 exact 판정과 binding, spectral 잔차 식.
- `numerically checked`: [S6_RESULTS_KO.md](S6_RESULTS_KO.md)의 r1/r2, held-out,
  native spectral run01, source-age 실행.
- `literature-supported`: Chebyshev 계수의 Bernstein ellipse 상한과 GL 수렴률은
  Trefethen, *Approximation Theory and Approximation Practice*, Thm 8.1, 19.3의
  표준 결과다. 이번 세션에서 원문을 다시 열어 확인하지는 않았다.
  Bianchi I 식은 S3에서 확인한 Fleury–Pitrou–Uzan Sec. IV A를 따른다.
- 새로운 전역 정리나 문헌 대비 신규성을 주장하지 않는다.
