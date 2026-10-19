# S8: 출생 기억을 포함한 결합계의 접선

작성 기준: 2026-10-19. 이 문서는 **실행 전의 유도·검증 계약**이다. 새 S8 소스에서 해석적 접선과 별도의 비선형 대칭 차분 궤적을 비교하도록 준비했다. 정식 campaign 결과는 별도 결과 문서와 불변 실행 receipt에 남긴다.

복구 기준 HEAD는 fe083a28e066a95e2191bcc6a090adf53605453f이다. S7 R1/R2의 실제 실패와 R3의 한 궤적 보정 PASS는 그대로 보존한다. 이번 단계는 이전 campaign을 재실행하지 않는다.

## 1. 물리 범위와 판별할 질문

범위는 non-tilted axisymmetric Bianchi I이고, 다음 관례를 고정한다.

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dX^2+dY^2)+a^2e^{4b}dZ^2,\qquad
s=\dot b,\qquad \Sigma=\sqrt3\,|s|/H .
\]

\[
x=\log(a/a_{\rm ref}),\quad h=H/H_\star,\quad y=s/H_\star,\quad
E=kU/H_\star^2,\quad \Pi=k\Delta P/H_\star^2,\quad
L=\Lambda c^2/(3H_\star^2),\quad k=8\pi G/(3c^2).
\]

여기서 \(\Delta P=P_\parallel-P_\perp\)이며 광자의 평균 압력은 \(U/3\)이다. S8의 대상은 양의 pressureless donor, collisionless photon cohorts, 상수 \(L\)로 닫힌 **제조된 검증 모형**이다. 실제 MD14 source의 피드백이나 고정 native spectral owner의 finite-bin 적분을 대신하지 않는다.

질문은 초기 전단 \(y_0\)을 바꿀 때 생기는 최종 전단의 미분을, 출생 시각의 기하와 새로운 각도 규칙의 변화까지 포함한 해석적 접선이 재현하는가이다. 측정된 두 궤적의 \(\delta(\Pi/h)\)를 Duhamel 적분하는 항등식은 이 질문에 대한 독립 검증이 아니다. 여기서는 접선 RHS에 유한차분이나 실행 후 측정된 forcing을 넣지 않는다.

광자의 보존된 공변 운동량과 Einstein–Vlasov moment 계층의 배경은 [Lee–Nungesser–Tod, arXiv:1911.04937v2](https://arxiv.org/html/1911.04937v2) §2.1–2.2와 연결된다. 우리의 donor, 이산 출생 및 KL 규칙은 명시적으로 추가한 검증 모형의 요소다. 읽은 원문 위치와 관례 대응은 [PRIMARY_LITERATURE.json](evidence_s8/PRIMARY_LITERATURE.json)에 있다.

## 2. 독립적으로 진화시키는 배경과 제약

출생 사이의 식은

\[
\begin{aligned}
h'&=\frac{-h^2-2y^2-E_d/2-E_\gamma+L}{h},\\
b'&=\frac yh,\qquad y'=-3y+\frac{\Pi}{h},\qquad E_d'=-3E_d .
\end{aligned}
\]

초기 한 번만 \(h_0=\sqrt{y_0^2+E_{d0}+E_{\gamma0}+L}\)를 사용한다. 그 이후 \(h\)는 일반 Raychaudhuri 식으로 독립 진화시킨다. 제약으로 \(h\)를 매번 다시 설정하지 않는다.

\[
C=h^2-y^2-E_d-E_\gamma-L,\qquad
E_\gamma'=-4E_\gamma-2b'\Pi
\]

를 직접 미분하면 \(C'=-2C\)이다. 따라서 \(C\)의 크기는 초기화 방법에 의해 강제로 0이 되는 양이 아니라 독립 진화와 광자 에너지 수송을 확인하는 잔차다.

출생 구간은 \(0\le x\le X_B=0.8\), 관측 끝은 \(x_{\rm end}=1.2\)이다. \(\Delta=X_B/K,\ u_j=(j+\tfrac12)\Delta\)에서 donor를 국소적으로 이전한다.

\[
E_{d,-}(u_j)=E_{d0}e^{-3u_j-\lambda j\Delta},\quad
w_j=E_{d,-}[-\operatorname{expm1}(-\lambda\Delta)],\quad
E_{d,+}=E_{d,-}e^{-\lambda\Delta}.
\]

\(w_j>0,\ E_{d,+}>0\)를 검사한다. 출생에서 donor는 \(w_j\)만큼 줄고 광자 에너지는 \(w_j\)만큼 증가하며 \(h,b,y\)는 연속이다. 이는 S7의 midpoint donor 모형을 그대로 가져온 것이다. \(\theta=y_0\) 또는 아래의 \(b_0\) gauge에 대해서는 \(u_j,w_j,E_d,L\)가 독립이므로 \(\partial_\theta w_j=\partial_\theta E_d=0\)이다.

## 3. 이동하는 출생 각도와 양의 KL 최적해

고정 native Legendre 좌표 \(m_i\)와 양의 GL weights \(w_i^{\rm GL}\)에서 출생 시각의 \(b_u\)에 따라 source-frame 방향을 만든다.

\[
\begin{aligned}
\mathcal R(b_u,m_i)&=\sqrt{e^{2b_u}(1-m_i^2)+e^{-4b_u}m_i^2},\\
\mu_i(b_u)&=m_i e^{-2b_u}/\mathcal R(b_u,m_i),\\
\widetilde q_i(b_u)&=w_i^{\rm GL}\mathcal R(b_u,m_i)^{-3},\qquad
q_i=\widetilde q_i/\sum_j\widetilde q_j .
\end{aligned}
\]

고정 \(m_i\)에서

\[
\mu_{i,b}=-3\mu_i(1-\mu_i^2),\qquad
(\log q_i)_b=6\{P_2(\mu_i)-\langle P_2\rangle_q\}.
\]

정규화 전 prior의 log score는 \(6P_2(\mu_i)\)이다. \(f_i=(P_2(\mu_i),P_4(\mu_i))^T\)라 두면

\[
f_{i,b}=\begin{pmatrix}
3\mu_i\mu_{i,b}\\
\tfrac12(35\mu_i^3-15\mu_i)\mu_{i,b}
\end{pmatrix}.
\]

새롭게 태어난 **명시적으로 isotropic인 source**에만 다음 양의 KL 최적화를 적용한다.

\[
\min_{\alpha_i>0}\sum_i\alpha_i\log(\alpha_i/q_i),\qquad
\sum_i\alpha_i=1,\quad \sum_i\alpha_i f_i=0 .
\]

기존 광자장과 물리적으로 anisotropic인 old stock에는 적용하지 않는다. Plus-sign dual 관례로

\[
\alpha_i=\frac{q_i e^{\lambda^T f_i}}{\sum_jq_j e^{\lambda^T f_j}}.
\]

정확한 내부 최적해의 특징 평균은 0이다. 저장된 binary64 최적해에서는 작은 비선형 잔차를 실제 측정하므로, 다음 계산은 평균을 임의로 0으로 치환하지 않고 실제 centered covariance를 사용한다.

\[
\begin{aligned}
g_i&=(\log q_i)_b,& a_i&=g_i+\lambda^T f_{i,b},\\
V&=\operatorname{Cov}_\alpha(f,f),&
V\lambda_b&=-\langle f_b\rangle_\alpha-\operatorname{Cov}_\alpha(f,a),\\
\alpha_{i,b}&=\alpha_i\left[
a_i-\langle a\rangle_\alpha+
(f_i-\langle f\rangle_\alpha)^T\lambda_b\right].
\end{aligned}
\]

마지막 두 식은 \(\partial_b\langle f\rangle_\alpha=0\)와 \(\partial_b\sum_i\alpha_i=0\)를 직접 연립한 것이다. 이동하는 \(f_b\)를 빼면 고정 제약면에 대한 미분을 다른 문제에 적용하게 된다.

**미분의 의미:** 양의 내부 지지에서의 매끄러운 이상적 KL 최적해를 저장된 부동소수점 근사 최적해에서 평가한다. 반복 solver의 종료 분기, binary64 반올림 함수 또는 feasibility 경계를 가로지르는 함수를 정확히 미분했다는 뜻이 아니다. \(\alpha_b\)에는 양수와 음수가 함께 나타나도 되며, 이는 signed derivative이다. 실제 광자의 weights \(\alpha_i\)에는 엄격한 양성을 요구한다.

일반적인 유한 이산 \(\phi\)-projection의 내부 미분 가능성과 암시적 Jacobian의 맥락은 [Geenens–Kojadinovic–Martini, arXiv:2407.05997](https://arxiv.org/pdf/2407.05997) Theorem 19, Corollary 31, Proposition 32 및 Appendix B와 비교한다. 그 원문의 고정 equality set 결과를 BASS의 이동 지지에 대한 기성 공식으로 인용하지 않는다. 위 \(f_b\) 항은 이 문제에 맞추어 직접 미분한 것이다. 신규성이나 전역 경계 미분 가능성을 주장하지 않는다.

### 내부 정칙성과 정확한 admission을 별도로 검사

기존 P24 projector 호출의 내부 정지 목표는 \(10^{-15}\)이다. 실제 저장된 \((\mu_i,\alpha_i)\)에 대한 admission은 S7에서 고정한

\[
\left|\sum_i\alpha_i P_\ell(\mu_i)\right|
\le \frac{3}{10^{15}},\qquad \ell=2,4
\]

를 그대로 유지한다. 왼쪽은 저장된 binary64 수를 정확한 dyadic 유리수로 읽어 Legendre 다항식과 합을 Fraction으로 계산한다. 정규화는 독립 항목이다. 내부 목표를 더 엄격하게 지정하는 것은 admission 허용오차를 넓히는 일이 아니다.

추가로 \(\lambda_{\min}(V)\ge10^{-10}\), \(\operatorname{cond}_2(V)\le10^8\)을 사전 고정한다. rank나 조건수 실패에 pseudoinverse를 넣지 않는다. projector의 support infeasibility, exact moment 초과, covariance 정칙성 실패, 미분 잔차 실패는 각각 구체적인 증거와 실패 종류로 남긴다.

### prior 미분만 뺀 음성 대조의 식별 한계

이 LRS prior의 raw score \(6P_2\)는 바로 제약 feature span 안에 있다. 이를 일관되게 제거하면 \(\lambda_{2,b}\)만 6만큼 이동하고 \(\alpha_b\)는 바뀌지 않을 수 있다. 따라서 “prior 미분을 빼면 반드시 실패해야 한다”는 검사를 만들지 않는다. 대신 아래의 기억·방향·weight 항을 각각 생략한 세 대조를 사용한다. 이 상쇄는 별도 개발 검사와 독립 유리수 fixture로 확인한다.

## 4. Collisionless kernel의 전체 편미분

출생 후에는 각 cohort의 \(b_u,\mu_i,\alpha_i\)를 고정한다. \(d=b(x)-b_u\)와

\[
W=e^{2d}(1-\mu^2),\quad V_r=e^{-4d}\mu^2,\quad
R=\sqrt{W+V_r},\quad D=(V_r-W/2)/R
\]

를 사용한다. \(V_r\)는 ray 성분이며 앞 절의 covariance \(V\)와 다르다. 필요한 편미분은

\[
\begin{aligned}
R_d&=-2D,\\
D_d&=-\frac{W^2+14WV_r+4V_r^2}{2R^3},\\
R_\mu&=\frac{\mu(e^{-4d}-e^{2d})}{R},\\
D_\mu&=\frac{\mu(e^{2d}+2e^{-4d})}{R}
-\frac{D\,\mu(e^{-4d}-e^{2d})}{R^2}.
\end{aligned}
\]

이 식과 source-frame Jacobian·prior score 및 제약의 접선 전파를 독립 Wolfram 계산에서 검산한 결과 8개 차이는 모두 0이었다. 원문 식, 가정, 도구 출력과 UTC는 [WOLFRAM_PARTIALS.json](evidence_s8/WOLFRAM_PARTIALS.json)에 있다. 새 개발 검사는 직접 정의한 complex \(R,D\)의 complex-step와 네 편미분을 비교한다. 이는 정식 결합 궤적 campaign의 대체물이 아니다.

## 5. 출생 기억을 가진 에너지·응력 접선

cohort \(j\)에 대해

\[
E_j=w_j e^{-4(x-u_j)}\sum_i\alpha_{ji}R(d_j,\mu_{ji}),\qquad
\Pi_j=w_j e^{-4(x-u_j)}\sum_i\alpha_{ji}D(d_j,\mu_{ji}).
\]

\(B=\partial_\theta b(x)\), \(B_j=\partial_\theta b(u_j)\)라 쓰자. S8의 \(\theta=y_0\)에서는 \(u_j,w_j\)가 고정이므로

\[
\begin{aligned}
\partial_\theta d_j&=B-B_j,\\
\partial_\theta \mu_{ji}&=\mu_{ji,b}B_j,\\
\partial_\theta \alpha_{ji}&=\alpha_{ji,b}B_j,\\
\partial_\theta E_j&=w_j e^{-4(x-u_j)}
\sum_i\big[\alpha_{ji,\theta}R+
\alpha_{ji}\{R_d(B-B_j)+R_\mu\mu_{ji,\theta}\}\big],\\
\partial_\theta\Pi_j&=w_j e^{-4(x-u_j)}
\sum_i\big[\alpha_{ji,\theta}D+
\alpha_{ji}\{D_d(B-B_j)+D_\mu\mu_{ji,\theta}\}\big].
\end{aligned}
\]

현재 \(B\)만 남기고 \(B_j\)를 버리면 출생의 기하 기억을 잃는다. 또한 \(B-B_j\)를 유지해도 새로운 출생 규칙의 \(\mu_b,\alpha_b\)를 빼면 실제로 변화시킨 source family의 미분과 달라진다.

old stock의 source-frame 분포는 \(\theta=y_0\)에 대해 고정한다. 그 경우 \(B_j=0,\ \alpha_\theta=\mu_\theta=0\)이지만 \(R_dB,D_dB\)에 의한 현재 기하의 수송 반응은 남는다. old physical anisotropy의 합법적인 반응을 0으로 지우지 않는다. physical old weights는 양의 GL128 rule에 \(1+0.4P_2\)를 곱해 정규화한 고정 분포다. old isotropic stock도 별도의 GL128 분포로 유지한다.

각 cohort에는 physical rule digest와 \((B_j,\mu_\theta,\alpha_\theta)\) memory digest를 함께 저장한다. 출생 이후 이를 다시 project하거나 수정하지 않았는지 readback 검사한다.

## 6. Einstein 접선과 출생의 일치 조건

이 문서의 prime는 \(x\) 미분이며, \(H_\theta=\partial_\theta h,\ Y_\theta=\partial_\theta y\)라 쓰면

\[
\begin{aligned}
H_\theta'&=\frac{-2hH_\theta-4yY_\theta-E_{\gamma,\theta}}h
-\frac{h'}hH_\theta,\\
B'&=\frac{Y_\theta}{h}-\frac{yH_\theta}{h^2},\\
Y_\theta'&=-3Y_\theta+\frac{\Pi_\theta}{h}-\frac{\Pi H_\theta}{h^2}.
\end{aligned}
\]

초기 전단을 변화시키되 \(H_\star\)와 \(x\)를 고정하므로

\[
(H_\theta,B,Y_\theta)_{x=0}=(y_0/h_0,0,1).
\]

초기 \(h_\theta=0\)으로 두지 않는다. donor, old source 에너지와 \(L\)가 고정된 상태에서 초기 Hamiltonian을 만족하려면 위 값이 필요하다.

출생 시각에서 \(d_j=0,\ B-B_j=0\), \(R=1\), \(R_\mu=0\)이다. 정규화 미분으로 \(E_{j,\theta}=w_j\sum\alpha_{ji,\theta}=0\)이고, P2 제약의 미분으로

\[
\Pi_{j,\theta}=w_j\sum_i\{\alpha_{ji,\theta}P_2(\mu_{ji})
+3\alpha_{ji}\mu_{ji}\mu_{ji,\theta}\}=0.
\]

따라서 \(h,b,y\)뿐 아니라 그 접선도 출생에서 연속이다. RHS는 새로운 cohort의 추가로 바뀔 수 있다. 실행에서는 에너지 점프의 접선, 압력 점프 및 출생 moment 미분 잔차를 각각 실제 수치로 저장한다.

제약의 접선은

\[
C_\theta=2hH_\theta-2yY_\theta-E_{\gamma,\theta}.
\]

\[
E_{\gamma,\theta}'=-4E_{\gamma,\theta}
-2\{b'\Pi_\theta+B'\Pi\}
\]

와 접선 Einstein 식을 결합하면 \(C_\theta'=-2C_\theta\)이다. 실행은 \(C_\theta\) 자체의 오차와 \(C_\theta'+2C_\theta\)를 각각 기록한다. 더불어 각 cohort의 \(E_{j,\theta}(x)\)를 \(x,b,B\) 방향으로 complex-step하여 마지막 에너지 식의 시간 미분을 독립적으로 검사한다.

## 7. 고정한 실제 campaign과 음성 대조

기본값은

\[
(E_{d0},E_{{\rm old,iso}},E_{{\rm old,phys}},L,y_0,b_0)
=(0.7,0.16,0.04,0.1,0.08,0.3),\quad
\lambda=0.7,\quad K=32,\quad n=16 .
\]

S8에서는 angular refinement나 \(K\) 수렴 시험을 동시에 수행하지 않는다. 동일한 하나의 support와 고정 출생 일정에서 미분 항의 효과를 판별한다. 다음 8개 적분만 사전 지정한다.

| 적분 | 수 | 실제 내용 |
|---|---:|---|
| 해석적 기본 궤적 | 1 | primal \(h,b,y\)와 full/세 omission 접선 열을 함께 적분 |
| 독립 비선형 대칭 차분 | 6 | \(y_0\pm\epsilon\), \(\epsilon=0.02,0.01,0.005\) |
| source-frame gauge | 1 | GL16, \(K=8\); \(\theta=b_0\), 모든 \(b,b_u\) 동시 이동 |

각 비선형 적분은 동결한 S7 solver를 사용하며 새 S8 출생 호출에서만 내부 \(10^{-15}\) 목표와 동일 exact admission을 적용한다. 미분 데이터는 비선형 solver에 전달하지 않는다. DOP853의 rtol \(5\times10^{-13}\), atol \(5\times10^{-15}\), max_step 0.08은 모두 고정한다.

비교 시각은 121개 균일 시각과 모든 출생 시각의 합집합이다. 차분 수렴과 omission 판정은 \(x\ge0.2\)에서 한다.

\[
D_\epsilon Q=\frac{Q(y_0+\epsilon)-Q(y_0-\epsilon)}{2\epsilon},\qquad
D_{\rm Rich}Q=\frac{4D_{0.005}Q-D_{0.01}Q}{3}.
\]

각 \(h,b,y,E_\gamma,\Pi,\Sigma\)의 접선과 차분 오차를 별도로 저장한다. \(\Sigma\)는 \(y\ne0\)인 이 fixture에서 \(\sqrt3[\operatorname{sign}(y)Y_\theta/h-|y|H_\theta/h^2]\)를 사용한다.

| 사전 판정 | 고정 목표 |
|---|---:|
| \(b,y\), joint \(h,b,y\) 차분 오차비 | 각 연속 \(\epsilon\) 쌍에서 3.5–4.5 |
| 가장 작은 \(\epsilon\)의 joint 오차 | \(\le2\times10^{-5}\) |
| 두 finest 차분의 Richardson joint 오차 | \(\le10^{-8}\) |
| 선형화 Hamiltonian·전파·cohort 에너지·출생 에너지 잔차 | 각 정규화 정의에서 \(\le10^{-11}\) |
| 미분된 P2/P4 제약 | 절대값 \(\le10^{-11}\) |
| gauge의 \(h_\theta,y_\theta,b_\theta-1\) | 각각 절대값 \(\le10^{-11}\) |

세 omission은 같은 primal에서 자기 자신의 접선 열을 진화시킨다. 새 birth memory도 각 열의 \(B_j\)에서 만들어 동결한다.

| 대조 | 생략하는 정확한 항 |
|---|---|
| omit_birth_memory | \(R_d,D_d\)의 \(-B_j\) 항만 생략; \(\mu_b,\alpha_b\)는 유지 |
| omit_mu_b | \(\mu_\theta=\mu_bB_j\) 방향 항만 0 |
| omit_alpha_b | \(\alpha_\theta=\alpha_bB_j\) weight 항만 0 |

각 대조의 \(y_\theta\) 오차가 가장 작은 \(\epsilon\)의 실제 차분 대비 \(\ge10^{-5}\)이고 동시에 full 접선의 같은 차분 오차의 100배 이상이어야 판별에 성공했다고 한다. 결과를 보기 전에 고정한 목표이며, 실패하면 판별 실패를 그대로 남긴다. 모든 omission이 반드시 Hamiltonian 보존을 깨야 한다고 요구하지 않는다. 다른 source family를 표현하는 일관된 반사실적 미분도 있을 수 있기 때문이다.

gauge 검사는 **source-frame GL 규칙에서만** 수행한다. \(b\)와 모든 \(b_u\)를 동시에 같은 양만큼 이동시키고 \(\mu,\alpha\)를 그대로 유지하면 \(d\)가 불변이다. 고정 native \(m\)에서 \(b_0\)만 바꿔 source-frame support까지 바뀌는 P24 family를 gauge라고 부르지 않는다.

## 8. 개발 검증, 소스 신원, 실행 경계

12개의 표적 개발 검사가 실제 통과했다. 네 kernel 편미분, 각도와 prior 미분, 국소 KL 접선, feature-span 상쇄, rank 실패, 독립 complex-step cohort 접선, old physical 수송, 국소 gauge, 2개 출생의 짧은 결합 smoke, source/contract 및 publication receipt 거부 경로를 포함한다. 단위 테스트 본체 0.244초, 별도 process wrapper 1.173초, 관측 RSS 83,360 KiB였다.

원 로그: [DEVELOPMENT_TESTS_R1.log](evidence_s8_tangent/DEVELOPMENT_TESTS_R1.log).
명령·시각·exit 0·8개 소스 SHA·resource cap·skill 적용 범위:
[DEVELOPMENT_TESTS_R1_RETURN.json](evidence_s8_tangent/DEVELOPMENT_TESTS_R1_RETURN.json).
짧은 \(K=2,\ x_{\rm end}=0.12\) smoke는 개발 검사이며 위 8개 정식 campaign을 실행했다는 뜻이 아니다.

별도 reviewer의 표준 라이브러리 Fraction/90자리 Decimal 구현은 24개 exact 검사와 7개 Decimal 검사를 통과했다. 이 독립 fixture는 BASS solver나 S7 테스트를 import하지 않는다. 이동 제약 항·prior-span 상쇄·old physical 수송 및 donor 제약 항등식을 뒷받침하지만 실제 S8 궤적 오차를 미리 인증하지 않는다. 증거는 [INDEPENDENT_TANGENT_CHECKS.json](evidence_s8/theory_review/INDEPENDENT_TANGENT_CHECKS.json)에 있다.

독립 코드 검토는 수학 blocker 없이 끝났으며 다른 repository/path/schema의 같은 바이트 receipt를 거르는 구체적인 guard 보완을 적용했다. 위 12개 테스트에 그 거부 경로가 포함된다. 검토 신원은 [PHYSICS_CODE_REVIEW.json](evidence_s8/theory_review/PHYSICS_CODE_REVIEW.json)이다.

새 구현은 다음 4개 파일이다.

- [s8_tangent_math.py](s8_tangent_math.py): 양의 KL implicit derivative와 kernel 편미분.
- [s8_tangent.py](s8_tangent.py): 동결 cohort memory, 독립 Einstein 접선과 진단.
- [run_s8_tangent.py](run_s8_tangent.py): 사전 계약, 게시 guard, 8개 적분 CLI.
- [test_s8_tangent.py](test_s8_tangent.py): 표적 개발 검사와 잘못된 게시 신원 거부.

coupled_cohorts.py, angular_balance.py, angular_p24.py, s6_io.py는 SHA-256이 고정된 기존 import다. 기존 source owner와 S7 파일은 수정하지 않는다. 정식 실행 전 불변 prereg와 8개 소스의 바이트를 Git commit에 게시하고 원격 ref/tree/blob readback을 수행한다. API receipt는 정확한 repository, schema, prereg path, commit, raw SHA-256, Git blob SHA, 8개 source SHA 및 원격 검증 여부를 모두 묶는다. source나 gate가 달라지면 CLI는 실행을 거부한다.

실행은 worker 1, BLAS/OMP/MKL 1, RAM 16 GiB, disk 4 GiB, job 1800초 상한을 사용한다. 결과 파일은 create-only로 남기며 failure가 발견되면 그 신원과 실패 종류를 보존한다. 필요한 NCP 실행은 같은 CLI의 정확한 committed prereg를 사용하도록 준비했다. parent의 게시/readback 확인 전에는 정식 campaign을 시작하지 않는다.

## 9. 이 단계의 승인 범위

이 단계가 통과하더라도 결론은 선택한 내부 support와 제조된 결합 모형에서 초기 전단 방향의 **출생 기억을 포함한 접선**이 비선형 차분·보존·음성 대조를 통과했다는 것이다. P2/P4 일치와 접선 일치는 continuum angular accuracy, native finite-bin photon/energy 보존, 실제 source/spectral-owner 피드백 또는 전 feasibility 영역의 미분 가능성을 승인하지 않는다.

물리적으로 anisotropic인 기존 광자장을 초기화하는 변경, REI production, full EoR, PR merge는 이 계약에 포함되지 않는다. 구체적인 실패에는 support 또는 알고리즘의 제한된 수선과 별도의 사전 계약을 사용하며 음의 physical weights, covariance pseudoinverse, admission 허용오차 완화로 우회하지 않는다.

