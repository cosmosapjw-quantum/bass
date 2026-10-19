# S7: 양의 source-age cohort와 Einstein 전단의 닫힌 결합

작성일: 2026-10-19. S6의 실제 실행 결과를 백업에서 먼저 받아 재사용한 뒤,
`COUPLED_FEEDBACK_CONTRACT.json`에 남아 있던 결합 의무를 진행했다.
이 문서는 새 결합식, donor closure, 독립 검산과 구현 계약을 소유한다.
실제 결합 solver의 campaign 판정은 별도 실행 receipt가 소유한다.

**결과.** 신규 photon source에 에너지를 공급하는 양의 pressureless donor를
함께 진화시키면, 고정 birth quadrature의 collisionless cohort를 Einstein 식과
일관되게 결합할 수 있다. 독립적으로 진화하는 Hubble 변수의 Hamiltonian
constraint는 source-free 구간에서 감쇠하고, donor와 photon 사이의 정확한
출생 에너지 전달에서는 연속이다. 이 구조를 Fraction 대수와 80자리 Decimal
기준해로 실제 검산했다.

## 1. 물리량과 source closure

범위와 convention은 non-tilted axisymmetric Bianchi I,

\[
ds^2=-c^2dt^2+a^2\bigl[e^{-2b}(dx_1^2+dx_2^2)+e^{4b}dx_3^2\bigr],
\quad H=\dot a/a,\quad s=\dot b,\quad
\Sigma=\sqrt3|s|/H
\]

다. 따라서 \(H_\perp=H-s\), \(H_\parallel=H+2s\),
\(\sigma^2=\tfrac12\sigma^i{}_j\sigma^j{}_i=3s^2\)다.
\(U_\gamma\)는 기존 stock과 신규 cohort를 모두 포함한 photon 에너지밀도,
\(\Delta P=P_\parallel-P_\perp\)는 그 압력차다.
각 massless ray에서 성립하는 trace 식 때문에
\(\bar P=(2P_\perp+P_\parallel)/3=U_\gamma/3\)이며,
\(\pi^i{}_j=\operatorname{diag}(-\Delta P/3,-\Delta P/3,2\Delta P/3)\)다.

닫힌 manufactured model은 압력 없는 comoving donor \(U_d>0\)를 두고

\[
\dot U_d+3HU_d=-Q,\qquad
\dot U_\gamma+4HU_\gamma+2s\Delta P=Q,\qquad
Q=\lambda H U_d,\quad\lambda\ge0                                      \tag{S7.1}
\]

를 사용한다. \(\lambda\)는 무차원 decay per log-scale factor다.
\(Q\)의 단위는 에너지밀도/시간이다. 두 식을 더하면 총 에너지 보존식에서
전달항이 정확히 소거된다. Reflection parity는 comoving momentum 전달을 0으로
유지한다. 여기서 donor는 실제 MD14 emissivity의 에너지 예산을 추정한 결과가
아니라, 결합 구현을 판별하기 위해 명시적으로 선택한 양의 닫힌 기준 모델이다.

Native spectral shape를 사용할 때 그 owner는 계속
`cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`이다.
해당 source shape와 에너지 정규화의 provenance를 유지하고, 이 manufactured
donor의 amplitude와 실제 owner emissivity를 구별한다. 실제 owner history를
full Einstein 모델로 도입하려면 그 에너지 공급/손실 성분도 총 stress-energy에
포함해야 한다. Prescribed emissivity만 photon 식에 추가한 모델의 결함은 §3의
constraint source term으로 직접 측정할 수 있다.

## 2. Metric에서 얻는 Einstein 식

\(k=8\pi G/(3c^2)\), \(L_0=\Lambda c^2/3\)라 두자. \(U\)와 압력이
에너지밀도 단위이므로 \(kU\), \(L_0\), \(H^2\), \(s^2\)의 단위가 모두
시간\(^{-2}\)다. \(\hbar\), \(k_B\)의 값은 이 stress-energy 평균과
무차원 ray kernel에서 상쇄되어 나타나지 않는다.

Directional rates를 사용하여 직접 계산하면

\[
G_{tt}=3(H^2-s^2),\qquad
c^2(G^3{}_3-G^1{}_1)=3\dot s+9Hs,
\]

\[
\frac{c^2}{3}\sum_iG^i{}_i=-2\dot H-3H^2-3s^2.
\]

Einstein 식 \(G_{ab}+\Lambda g_{ab}=8\pi G T_{ab}/c^4\)에 대입하면

\[
\boxed{H^2=s^2+k(U_d+U_\gamma)+L_0,}\qquad
\boxed{\dot s=-3Hs+k\Delta P.}                                      \tag{S7.2}
\]

00 Ricci 식, 즉 일반 Raychaudhuri 식은

\[
\boxed{\dot H=-H^2-2s^2-\frac{k}{2}U_d-kU_\gamma+L_0.}              \tag{S7.3}
\]

Constraint 위에서는 (S7.3)이
\(\dot H=-3s^2-\tfrac32kU_d-2kU_\gamma\)와 같다.
구현에서는 (S7.3)으로 \(H\)를 독립적으로 진화시킨다.
\(H=\sqrt{s^2+k(U_d+U_\gamma)+L_0}\)를 매번 대입해서 constraint 검사를
항등적으로 만드는 방식은 이번 검산에 사용하지 않는다.

고정 owner `rust/rei_microphysics/src/axbi_background.rs`의
`PhysicalDensityFixed`는 stress-free 배경에서 `hypot(H_FLRW,s)`를 사용한다.
같은 파일의 `omitted_feedback`는 (S7.2)의
\(k=8\pi G/(3c^2)\)를 사용하되 배경을 변경하지 않는 섭동 진단이다.
S7의 (S7.2)–(S7.3)은 실제 \(\Delta P\)로 기하를 진화시키는 새 연구 경로다.

## 3. 독립 Hubble 진화와 Hamiltonian 전파

\[
C=H^2-s^2-k(U_d+U_\gamma)-L_0
\]

로 두고 (S7.1)–(S7.3)을 미분·대입하면

\[
\boxed{\dot C=-2HC.}                                                 \tag{S7.4}
\]

즉 초기 constraint가 0이면 정확한 진화에서 계속 0이다.
Donor의 에너지 손실 \(-Q\)를 누락하고 photon에만 \(+Q\)를 넣으면

\[
\dot C+2HC=-kQ                                                       \tag{S7.5}
\]

가 된다. 이 식은 해당 입력 모델에 빠진 에너지 전달을 진단한다.
우변이 있는 모델을 닫힌 Einstein-source 모델로 채택하지 않는다.

구현을 위한 기준단위는 임의의 \(H_*>0\),
\(U_*=H_*^2/k=3c^2H_*^2/(8\pi G)\)이며

\[
x=\ln(a/a_{\rm ref}),\quad h=H/H_*,\quad y=s/H_*,\quad
E_d=U_d/U_*,\quad E_\gamma=U_\gamma/U_*,\quad
\Pi=\Delta P/U_*,\quad L=L_0/H_*^2
\]

다. \(h>0\)인 구간에서 prime을 \(d/dx\)로 정의하면

\[
\boxed{b'=\frac yh,\quad
y'=-3y+\frac\Pi h,\quad
h'=\frac{-h^2-2y^2-E_d/2-E_\gamma+L}{h},}                             \tag{S7.6}
\]

\[
E_d'=-(3+\lambda)E_d,\quad
E_\gamma'=-4E_\gamma-2\frac yh\Pi+\lambda E_d,
\quad C=h^2-y^2-E_d-E_\gamma-L,\quad C'=-2C.                         \tag{S7.7}
\]

여기서 \(\Sigma=\sqrt3|y|/h\)이고, source에 곱할 shear 변수가 \(y/h\)다.
\(s/H\)와 \(\Sigma\)를 혼용하면 shear source와 damping 계수가 바뀐다.

## 4. 고정된 cohort와 양의 midpoint 출생

각 cohort의 출생 좌표 \(u_k\), 당시의 \(b_k=b(u_k)\), 에너지 증분 \(w_k>0\),
source-frame 방향 \(\mu_{ki}\), weights \(\alpha_{ki}>0\)를 보관한다.
출생 때 정한 \(\mu_{ki}\), \(\alpha_{ki}\)는 이후 고정한다.
기존 stock과 물리적으로 비등방인 source의 분포도 원래 값으로 보관하며
새 isotropic source용 projection을 적용하지 않는다.

\[
E_\gamma(x)=\sum_k w_ke^{-4(x-u_k)}F_k(b(x)-b_k),\qquad
\Pi(x)=\sum_k w_ke^{-4(x-u_k)}G_k(b(x)-b_k).                            \tag{S7.8}
\]

\(F_k=\sum_i\alpha_{ki}R(d,\mu_{ki})\),
\(G_k=\sum_i\alpha_{ki}D(d,\mu_{ki})\)는 검증된 S3 kernel이다.
\(F'_k=-2G_k\)이므로 각 cohort는 source-free 구간에서
\(E_k'+4E_k+2(y/h)\Pi_k=0\)를 만족한다.
양성에서 \(E_k>0\), \(-1/2\le\Pi_k/E_k\le1\)이다.

상수 \(b\) offset의 coordinate gauge 검사는 현재 \(b\)와 모든 birth \(b_k\)를
함께 옮기고 source-frame 방향을 유지해서 수행한다. 이때 \(d=b-b_k\)는 같다.
고정 native coordinate grid의 ray label을 그대로 두고 절대 \(b\)만 바꾸면
source-frame support가 달라진다. 큰 \(|b|\)에서 그 grid의 quadrature가 어려워지는
것은 고정 owner grid의 conditioning 문제이며 coordinate-invariant 물리 배제
명제로 해석하지 않는다.

시간 격자폭 \(\Delta x\), 출생 수 \(K\),
\(u_k=(k+1/2)\Delta x\), \(k=0,\ldots,K-1\)의 midpoint impulse 모델을 쓴다.
출생 구간의 끝을 \(X_B=K\Delta x\)로 두고 관측은 그 뒤까지 계속할 수 있다.

\[
E_d(u_k^-)=E_{d0}e^{-3u_k-\lambda k\Delta x},\qquad
w_k=E_d(u_k^-)\,[1-e^{-\lambda\Delta x}],
\]

\[
E_d(u_k^+)=E_d(u_k^-)e^{-\lambda\Delta x},\qquad
E_\gamma(u_k^+)=E_\gamma(u_k^-)+w_k.                                  \tag{S7.9}
\]

출생 event에서 \(b,y,h\)는 연속이고 총 에너지 전달이 같으므로
\(C^+-C^-=0\)이다. 두 event 사이 donor는 \(E_d'=-3E_d\)로 진화한다.
출생 panel의 end point에서는 \(E_d(x)=E_{d0}e^{-(3+\lambda)x}\)가 정확하다.
출생 종료 후 \(x\ge X_B\)에는 \(E_d=E_{d0}e^{-3x-\lambda X_B}\)이고 신규 전달은 0이다.

이는 source-free coupled flow \(A\)와 donor→photon 전달 flow \(B\)의
\(A(\Delta x/2)B(\Delta x)A(\Delta x/2)\) Strang 구성이다.
\(h>0\), 매끄러운 kernel, 같은 양의 feasible projection branch에서 충분히
정칙인 birth rule을 전제로 source-age 이산화의 전역 오차는
\(O(\Delta x^2)\)다. 이 오차와 ODE 오차, angular 오차를 별도로 측정한다.
Birth support가 infeasible이거나 projection branch가 바뀌면 해당 가정을
확인하지 않은 것이므로 원래 feasibility 실패를 보존한다.

작은 \(\lambda\Delta x\)에서는 `-expm1(-lambda*dx)`를 사용한다.
\(\lambda=0\)은 cohort를 만들지 않는 no-source 극한이다.
수치 underflow로 donor나 포함된 ray weight의 양성이 소실되면 별도 실패로
기록한다. Weight를 clamp하거나 moment tolerance를 변경하지 않는다.

## 5. 실제 해를 구별하는 독립 기준식

### 5.1 Isotropic donor 기준해와 birth 차수

\(s=0\), 모든 cohort가 \(M_2=0\)이면 \(b\)는 상수이고 \(\Pi=0\)이다.
연속 donor의 해는

\[
E_d=E_{d0}e^{-(3+\lambda)x},\quad
E_\gamma=e^{-4x}\left[E_{\gamma0}
+\lambda E_{d0}\frac{e^{(1-\lambda)x}-1}{1-\lambda}\right],            \tag{S7.10}
\]

\(\lambda=1\)에서는 대괄호의 source 항이 \(E_{d0}x\)다.
이 식은 \(0\le x\le X_B\)에서 적용하며, 출생 종료 뒤에는
\(E_\gamma(x)=E_\gamma(X_B)e^{-4(x-X_B)}\)로 이어진다.
\(h=\sqrt{E_d+E_\gamma+L}\)는 이 기준해에서 독립적으로 계산하는 비교값이다.
Midpoint impulse source contribution과 연속 source contribution의 비는 정확히

\[
\frac{1-\lambda}{\lambda}
\frac{\sinh(\lambda\Delta x/2)}{\sinh((1-\lambda)\Delta x/2)}
=1+\frac{2\lambda-1}{24}\Delta x^2+O(\Delta x^4).                    \tag{S7.11}
\]

따라서 \(\lambda=1/2\)에서는 isotropic endpoint의 source energy가 모든
\(\Delta x\)에 정확히 일치한다. 일반적인 birth 2차 수렴 검사는 이 우연한
상쇄를 피해서 수행한다. 독립 Decimal 실행은 \(\lambda=0.4\),
\(x=1.2\), birth 수 8,16,32,64,128에서 오차비
3.999426, 3.999857, 3.999964, 3.999991을 얻었다.

### 5.2 Radiation-only의 실제 결합 선형 극한

\(E_d=L=Q=0\), shear와 stress 및 필요한 고차 angular moments의 등방 상태로부터의
편차가 함께 작은 collisionless radiation에서
\(q=s/H\), \(\mathcal A=\Delta P/U_\gamma\)라 두자.
\(\Omega_\gamma=1-q^2\), \(\dot H/H^2=-2-q^2\)이므로 정확한 shear 식은
\(q'=(1-q^2)(\mathcal A-q)\)다.
S3의 \(\mathcal A_d(0)=-8/5\)를 적용한 1차계는

\[
\begin{pmatrix}q\\\mathcal A\end{pmatrix}'
=\begin{pmatrix}-1&1\\-8/5&0\end{pmatrix}
\begin{pmatrix}q\\\mathcal A\end{pmatrix},\qquad
r_\pm=-\frac12\pm i\frac{3\sqrt{15}}{10}.                           \tag{S7.12}
\]

\(\omega=3\sqrt{15}/10\)라 하면

\[
q(x)=e^{-x/2}\left[q_0\cos\omega x+
 \frac{\mathcal A_0-q_0/2}{\omega}\sin\omega x\right],
\]

\[
\mathcal A(x)=e^{-x/2}\left[\mathcal A_0\cos\omega x+
 \frac{\mathcal A_0/2-(8/5)q_0}{\omega}\sin\omega x\right].            \tag{S7.13}
\]

이 기준은 fixed-background stress 적분과 달리, metric–radiation의 상호 작용에
따른 감쇠·진동을 함께 검사한다. 독립적인 직접 대입에서 80자리 중앙차분
ODE 잔차의 최댓값은 `3.866667e-24`였다.

Lee–Nungesser–Tod의 [arXiv:1911.04937v2](https://arxiv.org/html/1911.04937v2)
§2.1, Eq. (35)를 2026-10-19 실제 열어 확인했다. 그 논문은 \(8\pi G=c=1\),
양의 expansion-sign extrinsic curvature를 쓰며, 현재 세 번째 축을 parallel로
유지하면 \(q=2\Sigma_+\), \(\mathcal A=6w_+\)다. 이 대각 similarity가
논문의 계수 행렬을 (S7.12)로 옮기고 고유값을 보존한다.
작은 비등방성에서의 알려진 선형 결과를 구현 기준으로 사용한다.
Calogero–Heinzle의 [arXiv:0911.0667v1](https://arxiv.org/html/0911.0667v1)
§2의 일반 anisotropic-matter 식도 확인했으며, 그 논문의 반대 extrinsic-curvature
부호를 현재 \(s\)의 정의에 그대로 대입하지 않는다.

### 5.3 잔류 P4가 결합 선형 진동수를 바꾸는 방식

Radiation-only에서 frozen 양의 angular rule이 \(M_2=0\)을 만족하면,
\(b=\mathrm{constant}\), \(q=\mathcal A=0\)은 이 이산 모델의 normalized equilibrium이다.
그 에너지밀도와 주압력은 FLRW radiation 관계를 만족한다. 고차 angular moments가
남은 이 equilibrium 주위의 작은 \(\delta b,q,\mathcal A\)를 다루면 S3의 이미
검증된 kernel 미분에서

\[
q'=-q+\mathcal A,\qquad \mathcal A'=-\kappa q,\qquad
\kappa=\frac85-\frac{36}{35}M_4.                                    \tag{S7.18}
\]

이때 \(M_4\)는 equilibrium의 값이다. 수송으로 생기는 \(\delta M_4\)는
\(q\)와 곱해져 2차에 들어간다. 따라서 이 계수는 고정 rule의 선형 결합
응답을 결정한다. 양성, \(z=\mu^2\in[0,1]\), \(\langle z\rangle=1/3\)에서
\(1/9\le\langle z^2\rangle\le1/3\)이고

\[
-\frac7{18}\le M_4=\frac{35\langle z^2\rangle-7}{8}\le\frac7{12},
\quad 1\le\kappa\le2,
\]

\[
r_\pm=-\frac12\pm\frac{i}{2}\sqrt{4\kappa-1},\qquad
\frac{\sqrt3}{2}\le\omega\le\frac{\sqrt7}{2}.                       \tag{S7.19}
\]

즉 P2-only rule은 이 radiation-only 선형 문제에서 \(e^{-x/2}\) 감쇠를 유지하지만
잔류 P4가 진동수를 바꾼다. P2/P4를 맞추면 \(\kappa=8/5\),
\(\omega=3\sqrt{15}/10\)가 된다. S3의 양의
\(z=(1/6,1/2),\beta=(1/2,1/2)\) 예제는 \(\kappa=15/8\)을 준다.
범위의 양 끝은 각각 \(z=(0,1),\beta=(2/3,1/3)\)와 \(z=1/3\)에 놓인
양의 reflection-even 규칙으로 달성할 수 있다.

이는 고정 이산 quadrature equilibrium에 대한 직접 유도다. S7의 GL 기반
실제 radiation-only 선형 benchmark와 별도로, 임의의 잔류 P4를 둔 비선형
trajectory에서 (S7.19)를 측정한 실행은 그 전용 receipt가 있을 때 채택한다.

## 6. 응답 오차와 geometry feedback의 분리

서로 다른 두 실제 trajectory \(a,b\)의 signed shear 차이는 정확히

\[
\delta y(x)=e^{-3(x-x_0)}\delta y(x_0)
+\int_{x_0}^x e^{-3(x-v)}
 \left[\frac{\Pi_a(v)}{h_a(v)}-\frac{\Pi_b(v)}{h_b(v)}\right]dv.       \tag{S7.14}
\]

그 forcing은

\[
\frac{\Pi_a}{h_a}-\frac{\Pi_b}{h_b}
=\frac{\delta\Pi}{h_b}+\Pi_a\left(\frac1{h_a}-\frac1{h_b}\right)      \tag{S7.15}
\]

로 정확히 나뉜다. 첫 항도 실제 coupled histories의 \(\delta\Pi\)를 사용하면
geometry 변화를 포함한다. Prescribed background에서 rule만 바꿔 계산한
\(\delta\Pi\)는 별도 forcing 실험이다. 그 결과를 full tangent로 부르지 않는다.

완전한 1차 variation에는 \(b(u_k)\)의 출생 memory가 들어간다.
\(L_k=w_ke^{-4(x-u_k)}\)를 쓰고 donor·출생 schedule을 고정하면

\[
\delta E_\gamma=\sum_kL_k[F'_k\delta b(x)+B^F_k\delta b(u_k)+S^F_k\delta\epsilon],
\quad
\delta\Pi=\sum_kL_k[G'_k\delta b(x)+B^G_k\delta b(u_k)+S^G_k\delta\epsilon],
\]

\[
B^F_k=\sum_i\bigl[(\partial_{b_u}\alpha_i)R_i+
 \alpha_i R_{\mu i}(\partial_{b_u}\mu_i)\bigr]-F'_k                  \tag{S7.16}
\]

이며 \(B^G\)는 \(R,F\)를 \(D,G\)로 바꾼 식이다.
Native ray label에서 source frame으로 보낸 방향에는
\(\partial_{b_u}\mu=-3\mu(1-\mu^2)\)가 들어간다.
반면 source-frame 방향·prior를 외부 입력으로 고정한 manufactured family에는
그 미분이 0이다. 두 family를 구별한다.

\(S^F=\sum_i(\partial_\epsilon\alpha_i)R_i\)는 고정 support의 rule forcing이다.
새 birth projection의 \(\partial_{b_u}\alpha\)는 constraint를 미분해 계산해야 한다.
기존 stock은 birth data를 고정하므로 그 출생 variation과 rule forcing이 0이다.
이 자료로 full tangent 식은

\[
\delta b'=\delta y/h-y\delta h/h^2,
\quad\delta y'=-3\delta y+\delta\Pi/h-\Pi\delta h/h^2,
\]

\[
\delta h'=(-2-h'/h)\delta h-4y\delta y/h-\delta E_\gamma/h.           \tag{S7.17}
\]

(S7.16)–(S7.17)은 완결된 미분 계약이며, 실제 tangent solver의 구현·실행 상태는
해당 artifact로 따로 확인한다. 고정 배경의 `omitted_feedback`와의 대조에는
(S7.14)–(S7.15)를 사용할 수 있다.

## 7. 실제 독립 검산과 남은 구현 의무

실행 명령은 연구 경로에서 다음과 같다.

```bash
python3 evidence_s7/theory_review/independent_coupled_review.py \
  > evidence_s7/theory_review/INDEPENDENT_REVIEW.json
```

[독립 script](evidence_s7/theory_review/independent_coupled_review.py)는 BASS의
kernel, projection, coupled solver를 import하지 않는다. Python 표준 라이브러리의
Fraction polynomial 대수로 metric 성분, source cancellation,
\(C'+2C\), donor 누락항, 출생 jump, 문헌 행렬 대응과 (S7.18)–(S7.19)의
계수를 28개 exact 검사로
확인했다. 별도 80자리 Decimal 검사 5개도 통과했다.

| 독립 검사 | 실제 결과 |
|---|---:|
| Metric/constraint/전달 및 finite-rule 계수 대수 | 28개, exact defect 0 |
| Anisotropic old stock을 포함한 cohort 에너지식 | 최대 절대 잔차 `7.106116e-26` |
| Source-frame 상수 b gauge: 현재 b와 모든 birth b를 함께 이동 | 에너지·압력 변화 0 |
| 양의 midpoint donor, isotropic reference, birth 수 8→128 | 오차비 3.999426→3.999991 |
| \(\lambda=1/2\)의 endpoint 상쇄 판별 | exact ratio 1 |
| Radiation-only 선형 결합 기준해 | 최대 ODE 잔차 `3.866667e-24` |
| 첫 19개 대수·5개 Decimal 검사 실행 비용 | 0.03857초, peak RSS 10880 KiB, worker 1 |

근거는 [INDEPENDENT_REVIEW.json](evidence_s7/theory_review/INDEPENDENT_REVIEW.json)이다.
Finite-rule spectrum 계수 9개를 추가하기 전의 최초 실행은
[INDEPENDENT_REVIEW_R1.json](evidence_s7/theory_review/INDEPENDENT_REVIEW_R1.json)과
같은 경로의 `independent_coupled_review_r1.py`에 그대로 보존했다.
이 검산은 새 coding contract에 대한 실제 실행이며, S2/S3/S6의 완료 캠페인을
재실행하지 않았다. 새로운 전역 안정성 정리나 문헌 대비 신규성을 주장하지 않는다.

Solver는 같은 birth schedule에서 prior/P2/P24와 angular refinement를 비교하고,
같은 rule에서 birth 수와 ODE accuracy를 바꿔 오차 원인을 구별해야 한다.
Hamiltonian과 cohort energy gate는 원래 값을 유지한다. 보존식의 통과는 angular
continuum 정확도 또는 native finite-bin deposition의 추가 승인으로 사용하지 않는다.
실제 owner source-age, transport/absorption, 물리적 source energy budget과 native
Einstein 결합은 각각의 원본 입력과 실행으로 검증할 별도 의무다.
