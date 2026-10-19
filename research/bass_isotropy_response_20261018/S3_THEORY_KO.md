# S3: 출생 시 등방성 제약과 이후 collisionless 전단 응답

작성일: 2026-10-19. 물리 범위: non-tilted axisymmetric Bianchi I.
기준 구현: PR174의 P2-only projection `930406550ce6d4d1b2e87f016c5c18fba48c4ccd`.
기준 게시: `a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc`.
원 native REI owner: `0e25846433170d0f420c4cda44a0bedbf02cd177`.

**결과.** 신규 등방 source의 이산 출생 각분포에서 `M2=0`은 출생 순간의
압력 등방성을 맞춘다. 이후 자유수송의 선형 전단 응답에는 잔류 `M4`가
독립적으로 들어간다. `M2=M4=0`이면 선형 응답은 맞고, 다음 곡률 오차에
`M6`가 들어간다. 이 차이를 정확한 유도와 기존 projection 코드를 호출하지
않는 독립 유리수·80자리 Decimal 계산으로 확인했다.

## 1. 정의, source frame, 물리량

서명은 `(-,+,+,+)`이고

\[
ds^2=-c^2dt^2+a^2(t)\{e^{-2b(t)}(dx_1^2+dx_2^2)
                  +e^{4b(t)}dx_3^2\}.
\]

\(a_\perp=ae^{-b}\), \(a_\parallel=ae^{2b}\),
\(s=\dot b\), \(H=\dot a/a\), \(\Sigma=\sqrt3|s|/H\)를 사용한다.
\(x=\ln(a/a_{\rm ref})\)와 \(u\)는 각각 관측 시점과 출생 시점의
log-scale-factor 좌표이고

\[
d=b(x)-b(u),\qquad \mu=\mu_u,\qquad z=\mu^2
\]

다. 이후 식에서 \(\mu\)는 **출생 source frame의 고정 방향**이다.
native ray label \(\mu_0\), 출생 각도 \(\mu_u\), 현재 각도 \(\mu_x\)를
동일시하지 않는다. source 생성 시 계산한 양의 weights \(\alpha_i\)는 해당
cohort가 수송되는 동안 고정한다.

\[
A=e^{2d}(1-z),\quad B=e^{-4d}z,\quad R=\sqrt{A+B},\quad
D=\frac{B-A/2}{R}.
\]

공변 공간운동량 보존으로

\[
E_x=E_u e^{u-x}R,\qquad
\mu_x=\frac{e^{-2d}\mu_u}{R}.
\]

Bianchi I의 이 표현은 [Fleury–Pitrou–Uzan, Sec. IV A,
Eqs. (4.1)–(4.5)](https://www2.iap.fr/users/pitrou/publi/1410.8473.pdf)의
\(\beta_i=(-b,-b,2b)\) 특수화다. 그 논문의 관측 방향 부호는 여기서
사용하는 짝수 압력 kernel에 영향을 주지 않는다.

출생 시 angular–spectral factorization을 가정한 하나의 collisionless cohort에
대해 \(\langle f\rangle_\alpha=\sum_i\alpha_i f(\mu_i)\),
\(\alpha_i>0\), \(\sum_i\alpha_i=1\)을 정의하고

\[
F(d)=\langle R\rangle_\alpha,\quad G(d)=\langle D\rangle_\alpha,
\quad \mathcal A(d)=\frac{G(d)}{F(d)}
\]

라 쓴다. 물리적 에너지밀도와 압력차는

\[
U(x)=U_u e^{-4(x-u)}F(d),\qquad
\Delta P(x)\equiv P_\parallel-P_\perp
       =U_u e^{-4(x-u)}G(d).
\]

\(P_\perp\)는 두 횡방향의 각각의 주압력이다. 따라서
\(\mathcal A=\Delta P/U\)이고 \(P_\parallel+2P_\perp=U\)다.
\(U\)와 압력은 같은 단위이며 \(R,D,d,\mu,M_\ell,\mathcal A\)는
무차원이다. \(s,H\)의 단위는 시간의 역수다. 이 비와 ray map에는
\(\hbar\), \(k_B\)의 선택이 들어가지 않으며 자연단위를 가정하지 않았다.

## 2. kernel의 미분과 정확한 Legendre 전개

먼저 \(A'=2A\), \(B'=-4B\)이므로

\[
R'=\frac{A-2B}{R}=-2D. \tag{S3.1}
\]

이 식은 모든 유한 실수 \(d\), \(-1\le\mu\le1\)에서 정확하다.
\(d=0\)에서 \(R=1\), \(B-A/2=(3z-1)/2\)이므로
\(D(0,\mu)=P_2(\mu)\)다. 분자 \(N=B-A/2\)를 쓰면
\(N'(0)=-1-3z\), \(R'(0)=1-3z\)이고

\[
D'(0)=N'(0)-N(0)R'(0)
      =-\frac12-6z+\frac92z^2.
\]

이에 \(P_2=(3z-1)/2\),
\(P_4=(35z^2-30z+3)/8\)을 대입하여

\[
\boxed{D'(0)=-\frac85P_0-\frac{10}{7}P_2+\frac{36}{35}P_4.} \tag{S3.2}
\]

고차 미분은 \(R^2\)의 계수에서 독립적으로 얻었다. 즉
\(R=\sum_{n\ge0}r_n(z)d^n\), \(r_0=1\)에 대해

\[
r_n=\frac12\left[
\frac{2^n(1-z)+(-4)^n z}{n!}
-\sum_{k=1}^{n-1}r_kr_{n-k}\right],\qquad
D^{(n)}(0)=-\frac{(n+1)!}{2}r_{n+1}.
\]

그 결과

\[
\begin{aligned}
D(0)&=P_2,\\
D''(0)&=\frac{16}{7}P_0+\frac{12}{7}P_2
 -\frac{216}{77}P_4+\frac{216}{77}P_6,\\
D'''(0)&=-\frac{96}{35}P_0+\frac{200}{77}P_2
 -\frac{43632}{5005}P_4-\frac{864}{77}P_6+\frac{1728}{143}P_8.
\end{aligned} \tag{S3.3}
\]

다항식 형태의 별도 대입식은

\[
\begin{aligned}
D''(0)&=-\tfrac12+\tfrac{63}{2}z-\tfrac{135}{2}z^2+\tfrac{81}{2}z^3,\\
D'''(0)&=-\tfrac12-156z+837z^2-1296z^3+\tfrac{1215}{2}z^4.
\end{aligned}
\]

축 방향 \(\mu=1\)에서는 \(D=e^{-2d}\), 횡방향 \(\mu=0\)에서는
\(D=-e^d/2\)이다. 두 극한의 0–3차 미분이 위 식과 일치한다.
모든 kernel은 \(\mu\mapsto-\mu\)에 짝수다.

## 3. 정규화된 응답에서 P4와 P6가 맡는 역할

\(M_\ell=\langle P_\ell\rangle_\alpha\), \(M_0=1\)이라고 하자.
정확한 continuum 등방 기준은
\(\langle f\rangle_{\rm iso}=\frac12\int_{-1}^1f(\mu)d\mu\)이며,
모든 \(\ell>0\)에서 \(M_\ell=0\)이다.

\(F'=-2G\)에서

\[
\mathcal A=-\tfrac12(\ln F)',\quad
\mathcal A(0)=M_2,\quad
\mathcal A'(0)=G'(0)+2M_2^2,
\]

\[
\mathcal A''(0)=G''(0)+6M_2G'(0)+8M_2^3.
\]

따라서 출생 시 \(M_2=0\)을 맞췄을 때

\[
\boxed{\mathcal A'(0)=-\frac85+\frac{36}{35}M_4,}\qquad
\boxed{\mathcal A''(0)=\frac{16}{7}-\frac{216}{77}M_4
                                    +\frac{216}{77}M_6.} \tag{S3.4}
\]

즉 `P2=0`과 정확한 collisionless 선형 전단 응답은 서로 다른 조건이다.
이 출생 제약을 전제로 선형 응답이 continuum 값 \(-8/5\)와 같은 조건은
추가로 `M4=0`이다. 양성에서 \(\langle z^2\rangle\in[1/9,1/3]\)이므로
P2-balanced 규칙은 \(-2\le\mathcal A'(0)\le-1\)을 만족한다.
P4 잔류는 여기서 응답의 크기를 바꾼다.

\(M_2=M_4=0\)이면

\[
\mathcal A'''(0)=\frac{2208}{175}-\frac{864}{77}M_6
                                   +\frac{1728}{143}M_8.
\]

따라서 작은 \(d\)에서

\[
\mathcal A_{\rm iso}(d)
 =-\frac85d+\frac87d^2+\frac{368}{175}d^3+O(d^4),
\]

\[
\begin{aligned}
M_2=0:\quad
\mathcal A_\alpha-\mathcal A_{\rm iso}
 &=\frac{36}{35}M_4d
   +\frac{108}{77}(M_6-M_4)d^2+O(d^3),\\
M_2=M_4=0:\quad
\mathcal A_\alpha-\mathcal A_{\rm iso}
 &=\frac{108}{77}M_6d^2
   +\left(-\frac{144}{77}M_6+\frac{288}{143}M_8\right)d^3+O(d^4).
\end{aligned} \tag{S3.5}
\]

P2/P4를 맞추면 기울기가 맞지만 곡률은 P6에 의존한다.
일반적으로 \(D^{(n)}(0)\)는 \(z\)의 \(n+1\)차 다항식이며 최고
Legendre 차수는 \(2n+2\)다. `P2,...,P(2m)`의 일치는
\(\mathcal A\)의 \(m-1\)차 미분까지 맞춘다. 유한한 moment 제약은
이 국소 미분 정확도를 제공하며, 유한 \(d\) 구간의 오차는 실제 kernel
비교와 angular refinement로 따로 측정한다.

연속 출생 source에서도 같은 오차가 source-age 응답에 전달된다.
\(j_U(u)\,du\)를 기존 spectral owner가 주는 출생 에너지밀도 증분이라
하면 collisionless source contribution은

\[
\Delta P_{\rm source}(x)
 =\int^x du\,e^{-4(x-u)}j_U(u)
   G_{\alpha(u)}\bigl(b(x)-b(u)\bigr).
\]

각 출생에서 \(M_2(u)=0\)일 때 잔류 P4가 주는 선도 bias는

\[
\delta\Delta P_{\rm source}(x)
 =\frac{36}{35}\int^x du\,e^{-4(x-u)}j_U(u)M_4(u)
     [b(x)-b(u)]+O(d^2).
\]

이는 주어진 기하에서의 자유수송 응답이다. Einstein 전단 방정식과 결합한
궤적 오차의 크기는 해당 결합 실행에서 따로 측정한다. 기존 광자장의
초기조건 contribution은 이 source-only 보정으로 바뀌지 않는다.

### 판별 예제

아래 \(z\)별 weights는 `+mu/-mu` pair의 합이다. \(z=0\)은 한 ray다.
모두 양의 weights를 가지며 정확한 유리수 moment 계산을 사용했다.

| 각지지와 group weights | 출생 moment | continuum와 다른 응답 |
|---|---|---|
| \(z=(1/6,1/2),\ \beta=(1/2,1/2)\) | \(M_2=0,\ M_4=-77/288\) | \(\mathcal A'(0)=-15/8\); 오차 \(-11/40\) |
| \(z=(0,1/2,1),\ \beta=(2/5,8/15,1/15)\) | \(M_2=M_4=0,\ M_6=-11/80\) | \(\mathcal A''(0)=19/10\); 오차 \(-27/70\) |
| \(z=(0,3/5),\ \beta=(4/9,5/9)\) | \(M_2=M_4=0,\ M_6=-33/100\) | \(\mathcal A''(0)=34/25\) |
| GL4, \(b(u)=0\) | \(M_2=M_4=M_6=0,\ M_8=-143/490\) | \(\mathcal A_\alpha-\mathcal A_{\rm iso}=-(144/245)d^3+O(d^4)\) |

첫 예제는 P2 projection이 이미 목표를 만족하지만 선형 응답이 틀리는
사례다. 두 번째는 P2/P4를 맞춘 후 남는 P6의 영향을 고정 지지 위에서
구별한다. 이들은 isotropic source quadrature의 판별용 manufactured
규칙이며, 물리적으로 비등방인 source를 등방화하라는 실행 지시가 아니다.

## 4. 양의 P2/P4 제약의 정확한 feasibility

\[
M_2=0,\ M_4=0
\quad\Longleftrightarrow\quad
\sum_j\beta_j z_j=\frac13\equiv t,\quad
\sum_j\beta_j z_j^2=\frac15\equiv v,\quad \sum_j\beta_j=1.
\]

reflection pair와 중복 \(z\)를 group으로 합친 뒤 서로 다른 지지를
\(0\le z_1<\cdots<z_m\le1\)로 둔다. ray 전체의 엄격한 양성은 group
weights의 엄격한 양성과 동등하며 pair 내부는 원 prior 비율을 유지한다.

**정리.** 모든 group에 \(\beta_j>0\)인 해가 존재할 필요충분조건은
\((t,v)\)가 \(\{(z_j,z_j^2)\}\)의 convex hull의 relative interior에
속하는 것이다. 이 경우별 판정은 다음과 같다.

1. \(m=1\): \(v-t^2=4/45>0\)이므로 불가능하다.
2. \(m=2\): \(z_1<t<z_2\)이고
   \(v=(z_1+z_2)t-z_1z_2\)일 때만 가능하다. 이때
   \(\beta_1=(z_2-t)/(z_2-z_1)\),
   \(\beta_2=(t-z_1)/(z_2-z_1)\)로 유일하다.
3. \(m\ge3\): \(z_1<t<z_m\)이고

   \[
   L(t)<v<U(t),\quad
   L(t)=\max_{1\le j<m}\{(z_j+z_{j+1})t-z_jz_{j+1}\},\quad
   U(t)=(z_1+z_m)t-z_1z_m
   \tag{S3.6}
   \]

   일 때만 모든 weights가 양수다. \(L(t)\)는 \(t\)를 사이에 둔 인접
   두 지지점을 연결하는 선분에서 평가할 수 있다.

**증명.** 연속한 두 지지 \(a<b\)에 대해 모든 지지 \(z\)는
\((z-a)(z-b)\ge0\)이므로
\(\langle z^2\rangle\ge(a+b)t-ab\)다. 양 끝점에 대해서는
\((z-z_1)(z-z_m)\le0\)이므로
\(\langle z^2\rangle\le(z_1+z_m)t-z_1z_m\)다.
각 경계는 해당 두 점을 섞어 달성되므로 (S3.6)은 convex hull의 정확한
상·하 경계다. \(m\ge3\)이면 곡선 위 서로 다른 세 점은 일직선 위에
놓이지 않아 affine dimension이 2다. 전체 지지에 양의 질량이 있으면 각
proper supporting facet의 부등식이 엄격해진다. 반대로 내부 target에서
전체 지지의 임의의 양의 barycenter를 충분히 작은 양만큼 빼도 나머지가
hull 안에 남는다. 나머지의 nonnegative convex representation과 그
barycenter를 합치면 모든 지지에 양의 weights를 얻는다. \(m=2\)는
선분의 relative interior에 대한 직접 계산이며 위 식을 준다.

경계 위에서는 일부 지지에 0이 강제된다. 예를 들어
\(z=(0,3/5,1)\)에서는 target이 lower boundary에 놓여 \(z=1\)의
weight가 0이어야 한다. \(z=(0,3/10,3/5)\)에서는 upper boundary에
놓여 중간 지지의 weight가 0이어야 한다. 이 상태는 현재 full-positive
계약의 실패다. \(z=(0,7/10,1)\)는 lower hull 밖이고,
\(z=(0,1/4,1/2)\)는 upper hull 밖이므로 nonnegative 해도 없다.

rank1을 일괄 실패로 처리하지 않는다. \(z=(0,3/5)\) 또는 정확한
GL4 지지는 양의 해를 가질 수 있다. GL4는 서로 다른 두 \(z\)만 갖지만
target과의 affine compatibility를 만족한다. 임의의 float 입력에서 그
compatibility가 반올림 오차와 구분되지 않을 때에는 수치 판정의
불확실성을 보고한다. tolerance를 키워 exact hull의 바깥점을 안으로
간주하지 않는다.

이 결과는 고정된 각지지에서의 moment feasibility다. 양성 quadrature의
표준 convex geometry를 이 두 moments에 적용한 것이며 새로운 전역
물리 no-go 또는 문헌 대비 신규 정리로 주장하지 않는다.

## 5. KL projection의 계산식과 parity

정규화된 양의 prior \(q_i\)에서

\[
\min_\alpha \sum_i\alpha_i\ln(\alpha_i/q_i),\quad
\sum_i\alpha_i=1,\quad \langle P_2\rangle=\langle P_4\rangle=0
\]

를 푼다. full-positive feasible support에서는 minimizer가 양수다.
실제로 최소점에 0 성분이 있다고 가정하고 양의 feasible 분포를 조금
섞으면 그 성분의 \(\alpha\ln\alpha\) 방향미분이 \(-\infty\)가 되어
최소성에 모순된다. 내부에서 Lagrange stationarity는

\[
\alpha_i(\lambda)=\frac{q_i e^{\lambda_2P_{2i}+\lambda_4P_{4i}}}
 {\sum_jq_j e^{\lambda_2P_{2j}+\lambda_4P_{4j}}},\qquad
\partial_{\lambda_a}\partial_{\lambda_b}\ln Z
 =\operatorname{Cov}_\alpha(P_a,P_b)
\]

를 준다. 이 finite-support information projection의 유일성·exponential
representation은 [Csiszár–Shields, Theorem 3.2,
pp. 442–443](https://www.renyi.hu/~csiszar/Publications/Information_Theory_and_Statistics:_A_Tutorial.pdf)와
일치한다. 이 문서는 natural logarithm을 사용하며, 원전의 logarithm 밑
차이는 minimizer에 영향을 주지 않는다.

\(m\ge3\)에서는 covariance가 positive definite이므로 finite dual
multiplier도 유일하다. \(m=2\)의 compatible case에서는 weights는
유일하지만 두 multipliers에는 affine null direction이 있다. 그 경우는
지지의 실제 rank로 축소해야 한다.

한 가지 안전한 계산 형태는 \(\lambda_4\)를 고정하고 기존 P2 scalar
root로 \(\lambda_2\)를 정한 뒤 outer P4 root를 푸는 것이다. P2=0
곡선을 따라

\[
\frac{dM_4}{d\lambda_4}
 =\operatorname{Var}(P_4)
  -\frac{\operatorname{Cov}(P_2,P_4)^2}{\operatorname{Var}(P_2)}>0
\]

이며 full-rank 조건에서 bracketed scalar search를 지원한다. log-sum-exp,
원 moment residual과 양의 weight의 실제 검사를 사용한다. feasibility와
floating underflow 또는 root 불수렴은 별도 실패다.

prior가 reflection-even이면 모든 feature가 짝수이므로 보정된 weights도
reflection-even이다. 고정 support, 고정 prior에서 P2-only와 P2/P4의
차이를 먼저 측정하고, `n`을 바꾼 angular refinement 효과는 별도로
측정한다. KL 목적값의 감소·증가는 collisionless 구간 전체 오차의
최소화 보증으로 사용하지 않는다.

## 6. 보존식, 유효범위와 구현 경계

출생 이후 weights를 고정하면 (S3.1)로부터

\[
\dot U+4HU+2s\Delta P=0. \tag{S3.7}
\]

이는 \(\sigma^a{}_b=\operatorname{diag}(-s,-s,2s)\)에서
\(\sigma_{ab}\pi^{ab}=2s\Delta P\)인 photon energy equation이다.
ray별로 성립하므로 어떤 고정 양의 angular 규칙에도 정확한 항등식이다.
number density는 \(n\propto a^{-3}\)이다. 양의 weights는
\(-1/2\le\mathcal A\le1\)과 \(U>0\)도 보장한다.
생존한 field를 매번 재보정하면 \(\sum_i\dot\alpha_iR_i\) 항이
추가되므로 이 cohort의 고정-weight 보존식이 달라진다.

실수 \(d\)가 유한하면 \(R>0\)이고 모든 식은 정칙이다.
\(|d|\le d_*\)에서는 \(e^{-2d_*}\le R\le e^{2d_*}\)이므로
compact 구간의 미분과 평균의 교환, Taylor remainder의 uniform bound가
성립한다. 복소 \(d\)에서 \(R^2=0\)의 가장 가까운 가능한 해는

\[
d=\frac16\ln\frac{z}{1-z}+\frac{(2k+1)i\pi}{6},\quad 0<z<1.
\]

따라서 \(|d|<\pi/6\)의 모든 더 작은 닫힌 원판에서 kernel의 Taylor
전개는 \(\mu\)에 대해 uniform하다. 이 strip에서는 \(R\)의 실수부가
양수인 branch를 택할 수 있고 양의 평균 \(F\)도 0이 되지 않으므로
정규화 응답 역시 같은 국소 전개를 갖는다. 큰 실수 \(d\) 비교에는
잘린 Taylor 다항식 대신 원래의 \(R,D\)를 평가한다.

이 유도의 factorization 가정은 native finite-bin deposition의 증거가
아니다. spectral owner, bin 경계 및 native ray별 energy-panel 교집합을
고정한 채 보정 source의 실제 photon/energy ledger를 따로 검증해야 한다.
기존 photon stock과 물리적으로 anisotropic한 source는 변경 대상이 아니다.

## 7. 실제 검산과 근거 상태

독립 script는
`evidence_s3/theory_independent.py`이며 기존 BASS projection 또는 native
코드를 import하지 않는다. 실행 명령은 다음과 같다.

```bash
python3 research/bass_isotropy_response_20261018/evidence_s3/theory_independent.py > research/bass_isotropy_response_20261018/evidence_s3/theory_independent.json
```

- `derived`: (S3.1)–(S3.7), normalized-response 미분, 고정 지지 feasibility
  필요충분조건과 boundary/rank 분류.
- `numerically checked`: Python 표준 `Fraction`으로 0–3차 kernel 미분과
  Legendre 전개를 exact equality로 확인했다. 별도의 80자리 `Decimal`
  exp/sqrt 중앙차분에서 최대 미분 오차는 약 `2.075e-12`였다
  (`h=1e-7`; 이것은 이 유한차분 검산의 truncation 오차다).
- `numerically checked`: `z=k/10`, `k=0..10`의 크기 1–5인 모든
  1023개 지지에서 (S3.6)을 exact barycentric simplex 열거와 대조했다.
  full interior 482개, feasible rank1 2개, boundary-only 105개였으며
  나머지의 실패 이유도 JSON에 남겼다.
- `numerically checked`: 별도의 continuum 적분식
  \(F=e^d[\sqrt{1+\kappa}+J(\kappa)]/2\),
  \(J(\kappa)=\int_0^1(1+\kappa\mu^2)^{-1/2}d\mu\),
  \(\kappa=e^{-6d}-1\)을 Decimal로 평가했다. `h=0.001,0.0005,0.00025`에서
  위 표의 4-ray, 5-ray, GL4 응답 오차의 선도차수 `d`, `d²`, `d³`와
  각각의 계수를 독립적으로 확인했다.
- `literature-supported`: Bianchi I ray energy map과 finite-support
  KL information projection의 표준 성질. 위 두 저자 제공 원문을
  2026-10-19 실제 열어 해당 식·정리를 확인했다.
- 남은 구현 의무: 새 P4 알고리즘의 별도 실행·프로퍼티 검증, 각지지
  refinement와 제약 변경을 분리한 campaign, native 보정 source의 실제
  도입 및 finite-bin photon/energy 보존. 이 문서만으로 해당 실행을
  완료 처리하지 않는다. 상태의 실제 갱신은 `DAG.json`과 실행 receipt가
  소유한다.
