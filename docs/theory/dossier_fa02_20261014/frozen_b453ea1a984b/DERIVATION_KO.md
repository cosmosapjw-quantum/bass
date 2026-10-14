# FA-02: 같은 관측 cap의 rapidity·pointing 접선과 균일 나머지

## 1. 명제, 입력과 선택한 관측자 family

**FA-02 명제.** FA-01의 처방된 Kasner test sector와 같은 source·absorber·energy band에서, 아래의 두 매개변수 관측자 family는 고정 cap label 위의 해석적 행렬 적분으로 표현된다. 이 표현의 1차·혼합 2차 미분은 명시한 선형 전달 초기값 문제로 계산된다. 실제 실수 영역 전체에서 2차 Taylor 나머지는 행렬 trace norm으로 \(1250\|h\|_\infty^3\) 이하이다. 이 상계는 표본 미분의 최대값이 아니라, 입력의 해석적 majorant와 Cauchy 추정으로 증명한다. 근거 상태는 직접 유도·symbolic/numerical check·같은 작성자의 변경영역 검토다. 외부 독립 심사는 미실행이다.

부모의 실제 POST_INTEGRATION_DAG.json, NEXT_LOOP.json, FA01_MODEL.json과 FA.25를 입력으로 읽었다. 원래 Loop10의 21개 단위와 D9.1, FA-01 normal-cap 결과, F-ADT-FRAME-01 및 F-N-STIM의 종결 상태는 변경하지 않는다. 아래는 한 축의 pointing을 추가로 고정한 **새로운 두 매개변수 family**다. 모든 3차원 observer 운동을 수치 채택했다는 뜻은 아니다.

계량 부호는 \((-+++ )\), normal tetrad는 \((u,e_i)\), 광자는 미래 진행방향을 사용한다. \(x=t/t_o\in[1/2,1]\), \(p=(2/3,2/3,-1/3)\)를 유지한다. Detector event는 \(x=1\)로 고정하고
\[
 a=(\chi,\psi)\in\mathcal A=[-1/50,1/50]^2,\quad
 w_\chi=\cosh\chi\,u+\sinh\chi\,e_1,\quad
 c_\psi=(\cos\psi,\sin\psi,0)
 \tag{FA2.1}
\]
로 둔다. 물리 속도는 \(c\tanh\chi\); \(\psi\)는 radian이다. \(w_\chi\)의 tetrad는 회전 없는 \(e_1\)-boost로 정하고, cap은 그 하늘에서 \(c_\psi\)를 중심으로 같은 반경 \(0<\delta\le.02\)를 갖는다. Analyzer는 각 화소에서 **같은 tetrad의 \(e_{2,w}\)를 투영**한다. Pointing에 맞추어 추가 roll을 주지 않는다.

같은 energy band \(E_w/E_*\in[.98,1.02]\), \(x_i=1/2\)의 zero incoming coherency, source plateau \([.95,1.70]E_*\)를 유지한다. Normal tensor는
\[
 \mathscr P=\begin{pmatrix}0&0&0\\0&.7&.1+.05i\\0&.1-.05i&.3\end{pmatrix},\quad
 \mathscr K=\operatorname{diag}(.4,.4,.8),\quad
 J_2=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
 \tag{FA2.2}
\]
Physical source는 FA-01의 \(j_*(E/E_*)^2[1+.1E/E_*]\mathscr P\)의 screen restriction이며 absorber와 rotation의 길이 단위는 \((ct_o)^{-1}\)다. \(j_*\)는 photons/(m\(^3\) s J sr), dimensionless band coherency의 물리 integrated intensity는 \(ct_oE_*^2j_*(e_+-e_-)J\)다. 미지 경험적 provider 오차는 null이다.

## 2. 움직이는 aperture를 고정 label로 되당기는 정확한 사상

고정 label \(\ell=(\cos r,\sin r\cos\phi,\sin r\sin\phi)\), \(r\le\delta\)를 두고 \(m=R_3(\psi)\ell\)로 정의한다. \(m\)은 실제 observer sky의 방향이다. 역 aberration은
\[
 L=\cosh\chi+\sinh\chi\,m_1=E_n/E_w,\qquad
 n=\frac{(\sinh\chi+\cosh\chi m_1,m_2,m_3)}{L}.
 \tag{FA2.3}
\]
\(D=1/L\)라 하면 정확히
\[
 d\Omega_n=L^{-2}d\Omega_m=L^{-2}d\Omega_\ell,\qquad
 D^{-2}d\Omega_n=d\Omega_\ell.
 \tag{FA2.4}
\]
이다. 따라서 고정 label 적분에 area factor가 보이지 않는 것은 그 항을 버렸기 때문이 아니라, **변환 Jacobian과 FA.25의 가중치가 정확히 상쇄되었기 때문**이다. 원 normal sky의 영역은 \(\Omega_a=\{n:m_\chi(n)\cdot c_\psi\ge\cos\delta\}\)로 움직인다.

\(A(r)=(a(r),b(r))\)를 각 방향의 projected-\(e_2\) analyzer라 하면
\[
 a(r)=\frac{e_2-r_2r}{\sqrt{1-r_2^2}},\quad b(r)=r\times a(r),\quad
 \widetilde A=[I+(\cosh\chi-1)e_1e_1^T]A(m)
 -\sinh\chi\,n\,e_1^TA(m).
 \tag{FA2.5}
\]
마지막 항은 역 Lorentz 변환 후 normal time component를 0으로 만드는 null-gauge 항이다. 실수 영역에서 \(n^T\widetilde A=0\), \(\widetilde A^T\widetilde A=I\)이고 orientation도 유지된다. 원 analyzer와의 회전은
\[
 M=A(m)^T[I+(\cosh\chi-1)e_1e_1^T]A(n),\qquad
 \widetilde A=A(n)M^T.
 \tag{FA2.6}
\]
Null-gauge 항은 \(A(m)^Tm=0\)로 이 contraction에서 상쇄되지만 FA2.5의 4-vector 사상에서는 필요하다.

FA-01의 같은 ray carrier \(T_0(n),T_q(n)\)를 사용하면 새 관측함수는 정확히
\[
 \boxed{J_\delta(a)=\frac1{\Omega_\delta}\int_{r\le\delta}
 M\,[m_3T_0(n)+.1m_4 L T_q(n)]M^T\,d\Omega_\ell,\quad
 \Omega_\delta=2\pi(1-\cos\delta).}
 \tag{FA2.7}
\]
\(m_3=1.0004\), \(m_4=1.000800032\). Fixed detector band의 normal energy endpoints는 \(LE_\pm\)로 이동한다. 이 polynomial source에서는 그 이동이 \(L\) 항으로 적분되어 있다. 실제 source cutoff의 경계를 통과하지 않음을 §5에서 확인한다. \(\psi=0\)이면 FA.25, \(\chi=\psi=0\)이면 기존 FA-01 cap을 회복한다.

Normal-domain 표현의 밀도를 \(Q_a(n)=D^{-2}M[m_3T_0+.1m_4D^{-1}T_q]M^T\), 영역 속도를 \(V_i=\partial_i\Phi_a\circ\Phi_a^{-1}\)로 두면 Reynolds 정리는
\[
 \partial_iJ=\Omega_\delta^{-1}\!\int_{\Omega_a}
 [\partial_iQ_a+\operatorname{div}_{S^2}(Q_aV_i)]\,d\Omega_n,
 \quad
 \partial_j\partial_iJ=\Omega_\delta^{-1}\!\int_{\Omega_a}\mathfrak T_j\mathfrak T_iQ_a\,d\Omega_n,
 \quad\mathfrak T_iQ=\partial_iQ+\operatorname{div}(QV_i).
 \tag{FA2.8}
\]
두 번째 식에서는 \(\partial_jV_i\)도 미분한다. §3의 고정-domain 식은 이 경계·measure·integrand 미분의 정확한 합이다. 이를 다시 boundary error로 더하면 중복이다.

## 3. Energy·ray·screen·analyzer의 전체 1차·2차 미분

\(b=(\sinh\chi+\cosh\chi m_1,m_2,m_3)\), \(n=b/L\)로 쓰면 모든 \(i,j\in\{\chi,\psi\}\)에 대해
\[
 n_i=\frac{b_i-nL_i}{L},\qquad
 n_{ij}=\frac{b_{ij}-nL_{ij}-n_iL_j-n_jL_i}{L}.
 \tag{FA2.9}
\]
\(m_\psi=J_3m\), \(m_{\psi\psi}=J_3^2m\), \(m_\chi=0\)이고
\[
 \begin{gathered}
 L_\chi=\sinh\chi+\cosh\chi m_1,\ L_{\chi\chi}=L,\
 L_\psi=\sinh\chi m_{1,\psi},\
 L_{\chi\psi}=\cosh\chi m_{1,\psi},\ L_{\psi\psi}=\sinh\chi m_{1,\psi\psi},\\
 b_\chi=Le_1,\ b_{\chi\chi}=b_1e_1,\
 b_\psi=(\cosh\chi m_{1,\psi},m_{2,\psi},0),\
 b_{\chi\psi}=\sinh\chi m_{1,\psi}e_1.
 \end{gathered}\tag{FA2.10}
\]
Pure \(\chi\) 방향에는 \(n_\chi=e_1-n_1n\), \(n_{\chi\chi}=(2n_1^2-1)n-n_1e_1\)가 된다. 이는 고정 normal ray를 미분한 식이 아니다.

Inherited analytic screen을 \(B(x,n)B(1,n)^T\)로 표시하여, 관측자 analyzer에 직접 정렬한 screen을
\[
 \Sigma(x,a,\ell)=B(x,n)B(1,n)^T\widetilde A,\quad
 v=\sqrt{1-(1-x^2)n_3^2},\quad q=x^{-2/3}v,\quad
 e=(n_1,n_2,xn_3)/v
 \tag{FA2.11}
\]
로 쓴다. \(k=(-n_2,n_1,0)/\sqrt{1-n_3^2}\), \(B=(k,e\times k)\)이므로 전 식이 대수함수다. FA2.5·9를 미분하면 screen과 analyzer의 미분이 함께 나온다. 특히 \(a_x=1-x^2\)에서
\[
 v_i=-a_xn_3n_{3,i}/v,\qquad
 v_{ij}=-a_x(n_{3,i}n_{3,j}+n_3n_{3,ij})/v-v_iv_j/v.
 \tag{FA2.12}
\]
배경은 이번 family에서 고정되어 있고 source/absorber는 공간적으로 균질하므로 coordinate ray 위치의 spatial source derivative는 0이다. Direction·energy·screen 미분은 위 식에 남는다.

\(P_a=\Sigma^T\mathscr P\Sigma\), \(G_a=\frac12\Sigma^T\mathscr K\Sigma+.3e_1J_2\), \(W_a=m_3+.1m_4Lq\), \(B_a=W_aP_a\)로 정의한다. Observer-aligned 전달식은
\[
 F'=B_a-G_aF-FG_a^T,\quad F(1/2,a,\ell)=0,\qquad
 J_\delta(a)=\Omega_\delta^{-1}\int F(1,a,\ell)\,d\Omega_\ell.
 \tag{FA2.13}
\]
실수 매개변수에서 \(G_a\)는 실수행렬이라 \(G_a^T=G_a^\dagger\)다. \(\Sigma^T\Sigma=I\)와 \(\mathscr K\succeq.4I\)로 loss 하한은 .4, source는 PSD이고 정확한 cap 평균도 PSD다.

\(F_i=\partial_iF\), \(F_{ij}=\partial_i\partial_jF\)에 대한 새 초기값 문제는
\[
 F_i'=B_i-GF_i-F_iG^T-G_iF-FG_i^T,\qquad F_i(1/2)=0,
 \tag{FA2.14}
\]
\[
 \begin{aligned}
 F_{ij}'={}&B_{ij}-GF_{ij}-F_{ij}G^T-G_{ij}F-FG_{ij}^T\\
 &-G_iF_j-G_jF_i-F_iG_j^T-F_jG_i^T,\qquad F_{ij}(1/2)=0.
 \end{aligned}\tag{FA2.15}
\]
여기서 \(B_i=W_iP+WP_i\), \(B_{ij}=W_{ij}P+W_iP_j+W_jP_i+WP_{ij}\)이고 모든 matrix product를 같은 순서로 미분한다. \(\Sigma_{ij}\)와 \(L_{ij}\)를 누락하지 않는다. Stokes는 기존 \((I,Q,U,V)=(\operatorname{tr}J,J_{11}-J_{22},2\Re J_{12},-2\Im J_{12})\)다. 그 1·2차 미분은 각 \(F_i,F_{ij}\)의 cap 평균을 같은 analyzer로 읽는다.

## 4. 계산 가능한 비교식과 유효영역 전체의 uniform remainder

### 4.1 해석적 연장의 분모와 입력 majorant

\(\ell\)과 \(x\)는 실수 domain에 두고 \(|\chi|,|\psi|\le3/25=.12\)인 복소 bidisk에서 위 공식을 해석적으로 연장한다. 실제 source plateau 식을 연장하는 것이며 물리적 cutoff가 복소평면 전체에서 해석적이라고 가정하지 않는다. 복소 연장에서는 transpose와 고정 \(\mathscr P\)를 그대로 사용하고 positivity를 주장하지 않는다.

양의 Taylor 급수와 geometric remainder로 \(\cosh(.12)<1.008\), \(\sinh(.12)<.121\), \(e^{.12}<1.128\)이다. \(\delta\le.02\)에서 다음 **유리수 상계**가 성립한다.
\[
 \begin{gathered}
 |m_1-1|<.011,\quad |m_2|<.142,\quad |m_3|\le.02,\quad |L-1|<.131,\\
 |n_1-1|<.015,\quad |n_2|<.164,\quad |n_3|<.024,\\
 |(1-n_2^2)^{-1/2}|<1.014,\quad
 |(1-m_2^2)^{-1/2}|<1.011,\quad
 |v^{-1}|<1.001,\quad |(1-n_3^2)^{-1}|<1.001.
 \end{gathered}\tag{FA2.16}
\]
예를 들어 \(|L|>.869\), \(n_1-1=e^{-\chi}(m_1-1)/L\)를 사용한다. 제곱근은 1에서 연속인 branch다. 모든 분모는 이 bidisk에서 0이 아니므로 같은 branch가 유지된다.

FA-01의 **대수 screen 식**에 이 새로운 bound를 대입하면 normal-analyzer의 \(T\)에 대해
\[
 |T-I|\preceq_{\rm entries}
 \begin{pmatrix}.04570854&.00203157\\.00399510&.03023921\end{pmatrix},\quad
 \|T-I\|_2<.06,\quad \|s_3-(0,1)\|_2<.031,\quad |e_1-1|<.017.
 \tag{FA2.17}
\]
표의 수치는 위로 반올림한 표시이며 실행 JSON에 exact rational이 있다. 따라서
\[
 \|G_n-G_0\|_2
 \le .2(2\cdot.031+.031^2)+.3(.017)<.018,\qquad
 -.4+2(.018)=-.364<0.
 \tag{FA2.18}
\]
Normal-carrier 표현 FA2.7을 사용하여 \(|W|<1.183\), \(\|P\|_1=1\)로부터
\[
 \|F_n(1)\|_1\le\tfrac12(1.183)(1.06)^2<.665.
 \tag{FA2.19}
\]
이것은 기존 FA-01의 .4-radius 증명을 반복한 것이 아니라 **새 rapidity/pointing bidisk에서 해당 대수식을 평가한 bound**다. 원 normal core는 임의의 복소행렬에도 Schatten ideal 부등식으로 수축하고 양쪽 perturbation을 합산한다.

FA2.6에서 \(\|A(m)\|_2<1.15\), \(\|A(n)\|_2<1.175\), \(\|\operatorname{diag}(\cosh\chi,1,1)\|_2<1.008\)이므로
\[
 \|M\|_2<1.363,\qquad
 \boxed{\sup_{|\chi|,|\psi|\le.12}\|J_\delta(\chi,\psi)\|_1
 <.665(1.363)^2<\frac54.}
 \tag{FA2.20}
\]
각 analyzer bound는 \(A(r)\)의 여섯 entry를 \((e_2,e_3)\)와 비교한 Frobenius bound다. 따라서 bidisk 내부뿐 아니라 cap 전체와 모든 \(x\)를 덮는다. Sampled derivative maximum을 사용하지 않았다.

### 4.2 1차·2차 Taylor 정리

실수 영역 \(\mathcal A\)의 임의 점 \(a\), \(\|v\|_\infty=1\)에 대해 \(a+zv\), \(|z|\le.1\)는 위 bidisk에 들어간다. Banach-valued Cauchy 부등식은
\[
 \|D_v^kJ_\delta(a)\|_1\le k!\,\frac{5/4}{(.1)^k}.
 \tag{FA2.21}
\]
를 준다. \(a+th\in\mathcal A\)인 전체 선분에서 Taylor 적분 나머지를 적용하면
\[
 \boxed{\|J(a+h)-J(a)-DJ(a)h\|_1\le125\|h\|_\infty^2,}
 \tag{FA2.22}
\]
\[
 \boxed{\|J(a+h)-J(a)-DJ(a)h-\tfrac12D^2J(a)[h,h]\|_1
 \le1250\|h\|_\infty^3.}
 \tag{FA2.23}
\]
이다. 각각의 Pauli analyzer norm이 1이므로 모든 개별 Stokes scalar도 같은 상계로 제한된다. 비교에는 **exact Taylor coefficients**를 사용한다. 수치계수·구적 오차는 다음 절의 정밀화 진단과 별개이며 이 해석적 상계로 자동 인증하지 않는다.

### 4.3 실수 물리 영역과 종료 margin

\(r_m\le\delta+|\psi|\le.04\)이고 inverse aberration에서
\[
 r_n\le2\arctan[e^{.02}\tan(.02)]
 =.0408078315666\ldots,\quad
 |m_2|\le\sin(.04),\quad |n_3|\le e^{.02}\sin(.02).
 \tag{FA2.24}
\]
따라서 analyzer 분모는 \(\sqrt{1-m_2^2}\ge\cos(.04)=.999200106661\ldots\), normal analyzer도 \(\cos r_n>0\), horizontal screen과 \(v\)도 양의 하한을 갖는다. Ray의 directional expansion \(2/3-e_3^2>0\)여서 \(1\le q\le2^{2/3}\). 실제 source energy는
\[
 .98e^{-.02}\le E_n/E_*\le1.02e^{.02}2^{2/3},\quad
 m_{E,-}=.0105946998406\ldots,\quad
 m_{E,+}=.0481419460146\ldots
 \tag{FA2.25}
\]
만큼 plateau 경계에서 떨어져 있다. 이 영역, fixed incoming slice, 동일 absorber, fixed band·cap·analyzer가 실행 guard다. \(H^{-1}\)이나 redshift-root의 역수를 사용하지 않는다. 다른 spectrum cutoff·시간경계·opaque detector를 넣으면 그 의존성을 추가해야 한다.

## 5. 실제 finite-parameter 판별

`runtime/fa02.py`는 총차수 2의 두 매개변수 Taylor algebra를 구현한다. Coefficient 저장순서는 \[ (F,F_\chi,F_\psi,F_{\chi\chi}/2,F_{\chi\psi},F_{\psi\psi}/2) \] 이며 elementary inverse·square root·trigonometric map과 matrix products를 모두 convolution으로 미분한다. 미분계수 산출에 finite difference는 쓰지 않았다. \(6\times16\) cap·256 time steps와 \(10\times24\) cap·512 time steps를 비교했고, 가장 큰 coefficient matrix-entry 차이는 \(1.62\times10^{-14}\) 이하였다.

\(\delta=.02\), \(a_0=(.008,.010)\)의 실제 Stokes derivative는 다음과 같다.

\begin{center}\small\begin{tabular}{lrrrr}\toprule
계수 & $I$ & $Q$ & $U$ & $V$\\\midrule
값 & 0.495848214 & 0.228685869 & 0.0657266465 & -0.0485409202\\
$\partial_\chi$ & 0.0547026568 & 0.0255027299 & 0.00695898659 & -0.00534359219\\
$\partial_\psi$ & -0.00702720876 & -0.00713754165 & 0.000360994911 & 0.000478144018\\
$\partial_{\chi\chi}$ & 0.0542768424 & 0.025146396 & 0.00696651579 & -0.00531051823\\
$\partial_{\chi\psi}$ & 0.0127249817 & 0.0132269983 & -0.000740775511 & -0.000849896956\\
$\partial_{\psi\psi}$ & -0.702629421 & -0.713664967 & 0.036068839 & 0.0478128755\\
\bottomrule\end{tabular}\end{center}

기준 cap의 양의 \(J\)와 정상점 \((0,0)\)도 새 jet의 0차 forcing으로 계산했다. 정상점에서는 reflection symmetry로 \(J_\psi=J_{\chi\psi}=0\); 비중심 \(a_0\)에서는 mixed derivative가 비영이다. 이는 pointing과 boost를 독립적인 두 보정량으로만 합치면 빠지는 항이다.

변화 \(h=(r,-r/2)\)를 세 크기로 택했다. 모든 경우 기준과 끝점, 그 사이 선분이 같은 \(\mathcal A\)에 있다.

\begin{center}\small\begin{tabular}{rrrrr}\toprule
$r$ & $I_{\rm direct}$ & $\|R_1\|_1$ & $\|R_2\|_1$ & uniform bound\\\midrule
0.008 & 0.49630974105 & 5.27067e-06 & 8.95569e-08 & 0.00064\\
0.004 & 0.49608001714 & 1.3288e-06 & 1.12347e-08 & 8e-05\\
0.002 & 0.49596437954 & 3.336e-07 & 1.40685e-09 & 1e-05\\
\bottomrule\end{tabular}\end{center}

두 번째 잔차의 비는 7.9714580, 7.9857172로 3차 스케일링에 접근한다. 이 수치 비교는 interval-certified continuum computation이 아니다. 새 미분식의 첫·둘째·혼합 계수는 별도의 중심차분과도 대조했다. 예시로 \(10^{-3}\)의 순수 parameter-truncation 예산을 선택하면 \(\|h\|_\infty=.008\)의 uniform bound는 .00064이고 .00036이 남는다. 경험적 provider나 검출 calibration의 오차를 0으로 채운 총 예산이 아니다.

## 6. 판별·보존·후속 상태

동일한 finite parameter의 결과를 (a) observer-aligned screen의 새 전달식과 (b) normal-frame 두 carrier에 FA2.7의 \(M,L\)를 적용하는 별도 표현으로 비교했다. 고유 source norm·screen Gram·두 표현의 일치를 확인했다. 매개변수 의존 passive screen \(R(a)\)에는 \(F\to RFR^T\), analyzer도 같은 변환을 적용하면 값·1차·2차 pairing이 모두 같았다.

Negative controls의 새 관측 오류는 다음과 같다. Analyzer를 함께 회전하지 않으면 1차 pairing 오류 0.0549340304, energy sampling $L$의 미분을 제거하면 0.0545451141, normal-domain aperture를 고정하면 잃어버린 pointing derivative의 trace norm은 0.00716264196이다. 각각 실제로 비영임을 확인했다.

추가로 일정한 invariant occupation의 flat field에서 moving cap을 올바르게 계산하면 값이 일정하지만, normal-domain boundary를 고정하고 Jacobian만 미분하면 \(1+\cos\delta\)의 거짓 1차 항이 남는다. 이것은 boundary term 누락의 정확 판별이다.

Wolfram의 별도 symbolic 계산은 inverse aberration·measure cancellation·pointing·mixed quotient 6개 잔차를 0으로 확인했다. 실제 xAct는 observer-screen null-gauge map의 **첫째·둘째 미분을 포함한 8개 contraction**을 0으로 확인했다. xAct가 로드된 뒤 unqualified `$Version`이 package version을 반환한 metadata 문제는 원반환에 보존하고 metadata-only 요청에서 kernel version을 확인했다. 물리 검산은 반복하지 않았다. Local check 48개에는 rational bound, finite differences, negative controls가 포함되며 독립 실험 수로 합산하지 않는다.

\(\nabla_aN_s^a=R_s^{\rm phys}/c\), \(\nabla_aT_s^{ab}=Q_s^{b,\rm phys}/c\), 같은 사건의 \(R,Q\)와 leg/weight 미분, ABF의 \(\kappa_s\), 근사 제약의 \(D\mathcal C\,r\)는 부모와 같다. Observer 재표현과 pointing 변경은 새 collision source가 아니다. `SOURCE_CLOCKS.json`, `ABUNDANCE_MODEL.json`, 원래 `THEORY_DAG.json`과 ADT.1–15는 바이트를 유지한다. F-ADT-FRAME-01의 수정 S23이 현재 문턱 설명이다.

일반 fixed-label pullback·variation 구조는 모든 허용 Bianchi, VI\(_{-1/9}\), physical tilt와 smooth passive boost, 정칙 \(H=0\)에 사용할 수 있다. **FA2.16–25의 상수와 실제 수치는 이 Kasner·두 매개변수 family의 결과**다. 전 종류의 background에서 같은 constants를 승계하지 않는다. Empirical emissivity·absorber·magneto-optical·metric 오차는 null로 유지한다.

C1: family·단위·같은 cap/band/analyzer·IC. C2: exact pullback과 first/second IVP. C3: PSD/passivity·기저 pairing·same event 계약. C4: physical observer와 passive representation 구분. C5: finite-parameter 구성·uniform remainder·boundary negative control. C6: 네 Stokes 및 계산 가능한 종료 margin. 원래 21/21 완료와 FA-01을 유지하고 FA-02만 후속으로 종결한다. 별도 외부 심사는 pending이다.

## 출처와 재현 경계

[INPUT] 부모 `NEXT_LOOP.json`, `fa01/FA01_MODEL.json`, `fa01/manuscripts/FA01_KO.md` FA.25, 고정 source·abundance bytes. [REUSE] PNS·COT/OSM·AP-OPTICS 및 F-ADT-FRAME-01의 현재 설명. [L1] Fleury, Pitrou, Uzan, PRD 91, 043511 (2015), arXiv:1410.8473: Bianchi-I Sachs 형식의 선행 참고. [L2] Challinor, PRD 62, 043004 (2000), astro-ph/9911481: observer-dependent polarization 형식. 이번 외부 대조는 원문 초록·서지 수준이며 새로운 상계와 계수의 근거는 위의 직접 유도다. 최초성은 주장하지 않는다.

부모의 full scientific suite를 호출하지 않았다. 새 algebraic jet·cap quadrature·observer projection과 그 검증은 동봉 코드에서 실행했다. 전체 판본의 갱신은 문서 통합이며, 원격 백업/게시 여부는 과학적 완료와 분리한 실제 capability·operation receipt를 따른다.
