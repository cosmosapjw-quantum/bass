# FA-03: 비회색 흡수의 유한 band-moment 접선과 관측자 혼합 응답

2026-10-14. 선택한 구성적 연구 단위 R5와 그 단계의 검산 결과다. 외부 독립 심사와 새로운 전체 R1–R10 순회의 종결은 주장하지 않는다. 근거 상태는 **직접 유도, 실제 Wolfram/xAct 기호 검산, 경량 구현 검증**이다. 이 문서는 기존 I–VII dossier를 대체하지 않는 증보다.

## 1. 원본과 적용 영역

기준은 실제 복원한 `BASS_ALL_BIANCHI_FA02_20261014__b453ea1a984b.zip`, SHA256 `b453ea1a984bea55c83dd54a1545e9cd344d90a31ee2e72ab51cb338579e01d5`다. 같은 날짜의 `72569f6e...` archive는 다른 세 매개변수 family이며 동일 자료로 대체하지 않는다. 여기서는 b453의 두 매개변수 \((\chi,\psi)\), `reference/FA02_KO.md` FA2.1–25, 정확한 `reference/fa02.py`만 소비한다. 기존 21개 이론 단위, D9.1, FA-01·FA-02 종결, microscopic collision·source clock·abundance owner는 불변이다.

계량 부호는 \((-+++)\). Kasner 배경의 지수는 \((2/3,2/3,-1/3)\), 무차원 시간은 \(x=t/t_o\in[1/2,1]\). Source·absorber는 normal frame에 정지한다. \(u\cdot u=-1\), 물리 4-속도는 \(U=cu\), 관측자는 \(w=\cosh\chi\,u+\sinh\chi\,e_1\)이다. 관측자 변경은 물질 tilt를 도입하지 않는다.

고정 cap label \(\ell=(\cos r,\sin r\cos\phi,\sin r\sin\phi)\), \(0\le r\le\delta\), \(0<\delta\le .02\)에 대해
\[
 m=R_3(\psi)\ell,\quad L=\cosh\chi+\sinh\chi m_1,\quad
 n=\frac{(\sinh\chi+\cosh\chi m_1,m_2,m_3)}{L}. \tag{FA3.1}
\]
\(|\chi|,|\psi|\le .02\). Detector band는 \(e=E_w/E_*\in[e_-,e_+]=[.98,1.02]\)로 고정한다. 다음 스칼라 \(k\)는 wavevector가 아니라 rest-energy 배율이다.
\[
 v=\sqrt{1-(1-x^2)n_3^2},\quad k=Lx^{-2/3}v,\quad
 E_{\rm rest}/E_*=ek. \tag{FA3.2}
\]
Cap label과 detector energy를 고정한 미분이다. 따라서 boost·pointing을 미분할 때 \(k\), ray direction, screen, analyzer를 함께 미분해야 한다.

FA2.5–13의 관측자 정렬 screen \(\Sigma\)를 그대로 사용하여
\[
 P=\Sigma^T\mathscr P\Sigma,\quad
 H=\tfrac12\Sigma^T\mathscr K\Sigma,\quad
 G=H+\Omega,\quad \Omega=.3\widehat e_1J_2, \tag{FA3.3}
\]
로 둔다. \(\widehat e=(n_1,n_2,xn_3)/v\), \(J_2=\left(\begin{smallmatrix}0&-1\\1&0\end{smallmatrix}\right)\), \(\mathscr K=\mathrm{diag}(.4,.4,.8)\). \(\mathscr P\)의 nonzero 2×2 block은 \(\left(\begin{smallmatrix}.7&.1+.05i\\.1-.05i&.3\end{smallmatrix}\right)\)다. Source plateau는 \([.95,1.70]E_*\), zero incoming coherency at \(x=1/2\), 길이 계수 단위는 \((ct_o)^{-1}\)다.

## 2. 선택한 비회색 모델과 정확한 전달식

새 모델은 **흡수만**
\[
 \mathscr K(E_{\rm rest};\epsilon)
 =[1+\epsilon(E_{\rm rest}/E_*-1)]\mathscr K,
 \qquad |\epsilon|\le .1 \tag{FA3.4}
\]
로 바꾼다. Rotation \(\Omega\)를 같은 인자로 곱하지 않는다. Source, geometry, incoming slice, observer band와 analyzer는 고정한다. 이는 처방된 affine opacity 모델이며 LTE·Kirchhoff equilibrium·원자율의 정확도를 뜻하지 않는다.

Detector energy별 무차원 coherency는
\[
 F_e'=e^3(1+.1ek)P-GF_e-F_eG^T
 -\epsilon(ek-1)(HF_e+F_eH^T),\quad F_e(1/2)=0. \tag{FA3.5}
\]
실수 매개변수에서 \(G,H\)는 실수행렬이므로 transpose는 Hermitian adjoint와 같다. Source의 복소 polarization matrix \(P\)는 Hermitian이다. 복소 매개변수 연장에서는 transpose와 고정 \(\mathscr P\)를 유지한다. 매개변수를 복소켤레하면 해석성이 깨진다.

FA2.4의 \(d\Omega_n=L^{-2}d\Omega_\ell\)와 \(D^{-2}=L^2\)는 정확히 상쇄된다. 고정 label 적분에 이 Jacobian을 다시 곱하거나 독립 boundary error로 더하지 않는다. 최종
\[
 J=\frac1{\Omega_\delta}\int_{\rm cap}\langle F_e(1)\rangle_e\,d\Omega_\ell,
 \quad \langle f\rangle_e=\frac1{e_+-e_-}\int_{e_-}^{e_+}f(e)de. \tag{FA3.6}
\]
물리적 band-integrated intensity는 \(ct_oE_*^2j_*(e_+-e_-)J\)이고, \(j_*\)의 단위는 photons/(m³ s J sr)이므로 결과 단위는 W/(m² sr)다. \(c\)를 생략한 natural-unit 결과가 아니다.

실제 energy 범위는 \(.98e^{-.02}\le ek\le1.02e^{.02}2^{2/3}\), 즉 약 [.96059,1.65186]로 plateau 내부다. 전체 plateau에서도 흡수 인자는 \(1-.1(.70)\ge.93\). 양의 source와 positive absorption, skew rotation의 propagator 적분 표현은 실수 영역의 \(F_e\succeq0\), \(J\succeq0\)를 보존한다. 수치 clipping을 필요로 하는 주장이 아니다.

## 3. 정확히 닫히는 여섯 개의 행렬 초기값 문제

\(m_j=\langle e^j\rangle\)는 exact rational이다.
\[
 m_j=\frac{e_+^{j+1}-e_-^{j+1}}{(j+1)(e_+-e_-)},\quad
 (m_3,m_4,m_5,m_6)=
 \left(\frac{2501}{2500},\frac{31275001}{31250000},
 \frac{18775003}{18750000},\frac{109593802501}{109375000000}\right). \tag{FA3.7}
\]
\(\mathcal L_GX=GX+XG^T\), \(\{H,X\}=HX+XH^T\)를 정의하고
\[
 S_j=\langle e^jF_e|_{\epsilon=0}\rangle,\quad
 V_j=\langle e^j\partial_\epsilon F_e|_0\rangle,\quad
 W_0=\langle\partial_\epsilon^2F_e|_0\rangle
\]
로 두면 다음 **여섯 행렬**이 닫힌다.
\[
 S_j'=(m_{j+3}+.1m_{j+4}k)P-\mathcal L_GS_j,\quad j=0,1,2; \tag{FA3.8}
\]
\[
 V_j'=-\mathcal L_GV_j-\{H,kS_{j+1}-S_j\},\quad j=0,1; \tag{FA3.9}
\]
\[
 W_0'=-\mathcal L_GW_0-2\{H,kV_1-V_0\}. \tag{FA3.10}
\]
모든 초기값은 0이다. 증명은 FA3.5를 \(\epsilon\)에 대해 0,1,2회 미분하고 유한 band에서 적분하는 것이다. 계수와 해가 compact 영역에서 매끄럽고 지배되므로 미분·적분을 교환할 수 있다. 회색 기준점의 \(G,H,k,P\)는 \(e\)에 의존하지 않고, perturbation은 \(e\)의 일차식이다. 그래서 2차 미분까지 필요한 최고 기준 moment가 \(S_2\)로 끝난다.

**이것은 \(\epsilon=0\)에서의 미분에 대한 정확한 closure다. 유한 \(\epsilon\ne0\)의 전체 spectrum에 대한 6-moment exact closure가 아니다.** 유한 \(\epsilon\)에서는 \(S_j\)가 \(S_{j+1}\)와 계속 결합한다. 한 평균 에너지로 opacity를 대체하는 것은 다른 모델이다.

Observer 방향 \(\alpha=\chi,\psi\)의 혼합 응답은
\[
 \begin{split}
 (\partial_\alpha V_0)'={}&-\mathcal L_G(\partial_\alpha V_0)
 -\mathcal L_{\partial_\alpha G}V_0
 -\{\partial_\alpha H,kS_1-S_0\}\\
 &-\{H,(\partial_\alpha k)S_1+k\partial_\alpha S_1-\partial_\alpha S_0\}.
 \end{split}\tag{FA3.11}
\]
\(S_j\)의 observer 미분은 FA3.8의 product rule이다. \(\partial_\alpha k\)를 누락하면 local-rest energy에서 정의한 opacity slope가 detector-fixed slope로 잘못 바뀐다. 구현은 총차수 2 observer Taylor algebra를 재사용하며 coefficient 순서는 \((1,\chi,\psi,\chi^2,\chi\psi,\psi^2)\)다. 대각 2차 미분은 저장 coefficient의 2배, mixed는 그대로다. \(W_0\)는 Taylor coefficient가 아니라 실제 2차 derivative다.

## 4. 세 매개변수 전체에서의 균일 나머지

복소 \(|\chi|,|\psi|\le .12\), \(|\epsilon|\le .2\)를 택한다. 동일 b453 family에서 이미 증명한 FA2.16–20의 분모·screen bound를 소비한다. 특히 \(|L-1|<.131\), \(|v-1|<.001\), \(|v|<1.001\), \(\|G_n-G_0\|<.018\), \(\|s_3-(0,1)\|<.031\)이다.

Normal analyzer에서 \(H_n=.2I+.2s_3s_3^T\)이므로
\[
 \|H_n\|\le.2+.2(1.031)^2=.4125922<.413.
\]
실수 \(e,x\)에 대해 \(ex^{-2/3}\le1.62\)이고
\[
 |ek-1|\le .62+1.62(.131\times1.001+.001)
 =.83405222<.85. \tag{FA3.12}
\]
따라서 \(\|G_{n,\epsilon}-G_0\|<.018+.2(.85)(.413)=.08821\). 원 loss .4에 대해 양쪽 perturbation을 합쳐도 \(-.4+2(.08821)<0\)이다. 복소 extension의 normal propagator도 Schatten trace norm에서 수축한다. Source bound와 analyzer map bound를 적용하면
\[
 \sup\|J\|_1\le\tfrac12(1.183)(1.06)^2(1.363)^2
 =1.2346907404286<5/4. \tag{FA3.13}
\]
복소 extension에서 positivity를 사용하지 않았다. Source plateau의 다항식 branch만 연장하며 cutoff가 해석적이라고 가정하지 않는다.

실수 box \(\mathcal B=[-.02,.02]^2\times[-.1,.1]\)의 모든 점에서, \(\|v\|_\infty=1\)인 실수 방향의 복소 disk 반경 .1은 위 영역 안에 있다. Banach-valued Cauchy 추정과 실수 선분의 Taylor 적분 나머지에 의해, 선분이 \(\mathcal B\) 안에 있으면
\[
 \|R_1(h)\|_1\le125\|h\|_\infty^2,\qquad
 \boxed{\|R_2(h)\|_1\le1250\|h\|_\infty^3.} \tag{FA3.14}
\]
각 Stokes analyzer의 operator norm이 1이므로 개별 Stokes에도 같은 상계가 적용된다. 이는 **정확한 Taylor coefficient**의 analytic remainder다. 수치 계수의 오차, 구적 오차, empirical provider error를 자동 포함하지 않는다. 실제 수치값은 아래의 별도 검산으로만 제한한다.

## 5. 실제 구현과 판별 결과

`code/fa03.py`는 FA3.8–10과 observer jet를 구현했다. `solve_energy`는 유한 \(\epsilon\)의 독립 energy-resolved quadrature 비교다. \((\chi,\psi,\epsilon)=(.008,.010,0)\), \(\delta=.02\), RK4 64 steps, cap GL3×12, energy GL8에서 intensity는 \(I=.49584821383969235\)이고
\[
 I_\epsilon=-.009092488124914306,\quad
 I_{\chi\epsilon}=-.07083361983984066,\quad
 I_{\psi\epsilon}=.00010846659661441795,\quad
 I_{\epsilon\epsilon}=.0003635939620156084.
\]
전체 I,Q,U,V와 행렬 jet는 `evidence/FA03_CHECKS.json`, `fa03_jet.npz`에 있다. 회색 원본 jet와 최대 entry 차이는 \(1.74\times10^{-18}\). Energy-resolved centered difference와 slope, 2차 slope 차이는 각각 \(3.52\times10^{-12}\), \(7.03\times10^{-10}\). Time 64→128과 cap GL3×12→GL5×20 변경에 대한 최대 state 차이는 각각 \(1.03\times10^{-11}\), \(1.39\times10^{-16}\)다.

\(h=r(.3,-.15,1)\), \(r=.02,.01,.005\)에서 quadratic remainder trace norm은 \(3.2524\times10^{-8},4.0777\times10^{-9},5.1048\times10^{-10}\)로 약 8배씩 감소했다. 이것은 차수 판별의 수치 증거이며 uniform theorem의 증명 대신 쓰지 않았다. 시험한 finite solution의 최소 eigenvalue는 .1265보다 컸다.

Energy GL1 midpoint surrogate는 같은 finite case에서 GL8과 \(2.17\times10^{-4}\) 차이를 보였다. 이 negative control에는 source band integration의 차이도 포함되므로 opacity averaging만의 오차라고 분해하지 않는다. 11개 사전 코드 기준이 충족되었다. Grey recovery 하나에 한해 실패 후 구현·통과의 TDD 기록이 있고 나머지 과학 검산은 별도 test-after다.

## 6. 원전 및 적용 경계

Fleury, Pitrou & Uzan, Phys. Rev. D 91, 043511 (2015), arXiv:1410.8473의 §§II–IV, 식 (24)–(28)은 Bianchi I conserved covariant momentum과 정확한 redshift의 원전이다. Gammie & Leung, ApJ 752, 123 (2012), DOI 10.1088/0004-637X/752/2/123의 coherency transport, 그리고 Huang et al., arXiv:2407.10431의 §2는 covariant transfer와 screen projection의 문헌 근거다. 이 문서의 six-matrix derivative construction과 위 상계는 이들 문헌에서 인용한 정리가 아니라 지정된 dossier family에 대한 직접 유도다. 광학 근사의 바깥인 파동분산 결과를 이 null-geodesic 모델에 섞지 않았다.

입자 tilt, geometry feedback, 실제 원자 opacity, scattering gain, 시간경계 변화, source cutoff crossing, 다른 observer roll 및 전천 sky로의 확장은 각각 별도 의무다. 특히 REI homogeneous scalar의 선형 shear 소거 정리를 이 finite cap observable에 적용해서는 안 된다.
