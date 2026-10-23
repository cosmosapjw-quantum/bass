# BASS 배경 진화: 이론 검산과 수정 계약

검토일: 2026-10-23 (Asia/Seoul). 독립 검토자: background_theory.
실제 읽은 저장소 HEAD: 797d66580448dad7fc41f2c2db31fe0eb37908bf.
대상 파일: bianchi/charts/general.py, bianchi/charts/general_matter.py,
bianchi/constraint_rates.py, bianchi/conventions.py.

## 결론

현재 general_matter의 Ω 진화는 radiation EOS γ=4/3에 맞춰져 있다. 일반 비틸트 γ-law에는 계수 (2q+2−3γ)가 필요하다. 회전 프레임의 Q 진화에는 +WQ가 필요하다. 두 수정은 물질 보존식에서 직접 정해지며, 임의의 pressure 입력과 회전 및 Jacobi 결함까지 포함한 정확한 다항식 항등식으로 검산했다.

공간곡률 닫힌 식은 저장소의 Koszul/Riemann 구현과 독립적인 exact-rational 계산 24건에서 일치했다. proper-time 또는 고정 reference-scale 변수로 옮기면 H로 나누지 않고 같은 배경계를 사용할 수 있다.

## 1. 원전·검산 근거

- H. van Elst & C. Uggla, *General Relativistic 1+3 Orthonormal Frame Approach Revisited*, arXiv:gr-qc/9603026v1; journal version CQG **14** (1997) 2673–2695, DOI 10.1088/0264-9381/14/9/021.
- 원전 URL: https://arxiv.org/pdf/gr-qc/9603026
- 직접 확인한 식: (2.8) 구조상수, (2.26)–(2.34) Einstein/Jacobi, (2.48)–(2.49) 물질 보존, (2.57) tilted-fluid 투영; SH 정규화 식 (4.223)–(4.237).
- PDF page 6을 직접 렌더링해 전사 과정에서 사라지는 부호·지수를 확인했다. 원전의 normalized 변수는 일부 Θ 기반이며, 아래 식은 BASS의 H 기반 변수로 직접 변환했다.
- SciSpace와 Exa를 실제 검색했다. SciSpace 검색 결과에는 arXiv:gr-qc/0210031, gr-qc/0304002의 부정확한 연도 metadata가 있으므로 source identity로 원전을 확인해야 한다.
- check_constraint_propagation.wl: dimensional 전체 defect 전파의 Wolfram exact symbolic 잔차가 각각 0, {0,0,0}, {0,0,0}.
- check_normalized_constraints.wl: 독립 q 입력의 Raychaudhuri 불일치 항까지 포함한 normalized 잔차가 각각 0, {0,0,0}, {0,0,0}.
- check_curvature_fraction.py: Python 표준 Fraction으로 C→Koszul→Riemann→Ricci를 별도 계산했다. 11 families와 exceptional VI_{−1/9}, 각각 canonical frame 및 유리수 SO(3) 회전: 24건 모두 정확한 0 잔차.
- 이번 환경에서 Python 실행은 성공했다. SymPy import는 PACKAGE_MISSING이었다. 그 부분은 Wolfram exact 검산으로 수행했으므로 연구 차단 상태가 아니다.

원전의 일반식은 literature-supported이고, 단위·정규화 변환과 defect factorization은 derived 및 symbolically checked다. 유한한 24개 curvature 사례는 exact arithmetic으로 checked된 표본이며 일반 항등식의 증명을 대체하지 않는다. 일반 curvature 식은 Koszul 전개와 원전 (2.30)–(2.32)에도 연결된다.

## 2. Convention 및 단위

metric signature (-,+,+,+), ε123=+1, normal frame n=e0, spatial homogeneity를 사용한다. normal congruence의 가속도·vorticity는 0이다. matter 유체는 normal에 대해 tilted일 수 있고 그 효과를 normal-frame μ,p,q,π로 입력한다.

\[
[e_i,e_j]=C^k{}_{ij}e_k,\qquad
C^k{}_{ij}=\epsilon_{ij\ell}n^{\ell k}+a_i\delta_j^k-a_j\delta_i^k .
\]

기하 시간은 \(\ell=ct\), prime은 \(d/d\ell\). \(H=H_{\rm physical}/c\), \(\sigma=\sigma_{\rm physical}/c\)이며 H,σ,n,a의 단위는 길이^{-1}이다. \(\sigma^2=\frac12\sigma:\sigma\).
\(\kappa=8\pi G/c^4\), μ,p,q,π의 단위는 energy density이다. 실제 에너지 flux는 \(c q\)다.

\[
T_{ab}=\mu n_an_b+2n_{(a}q_{b)}+p h_{ab}+\pi_{ab},
\quad q_an^a=0,\quad \pi_{ab}=\pi_{(ab)},\quad\pi^a{}_a=0 .
\]

\(W\)는 BASS의 COMMUTATOR convention에 따른 반대칭 프레임 생성자로 \(W x=R\times x\), \(W_{ij}=-\epsilon_{ijk}R_k\).
모든 spatial vector의 진화에 +Wv, symmetric tensor의 진화에 [W,X]가 들어간다.

## 3. 공간곡률 및 dimensional Einstein–matter 계

\(A_\times x=a\times x\), \(B=2n^2-\operatorname{tr}(n)n\)라 하면

\[
{}^3R=-6a^2-\tfrac12\operatorname{tr}B,\qquad
{}^3S=B-\tfrac13\operatorname{tr}B\,I+[A_\times,n].
\]

이는 \({}^3R_{ij}=B_{ij}-\frac12\operatorname{tr}B\,\delta_{ij}
-2a^2\delta_{ij}+[A_\times,n]_{ij}\)와 동치다.
Jacobi 조건은 \(na=0\).

\[
H'=-H^2-\tfrac23\sigma^2-\frac{\kappa}{6}(\mu+3p)+\frac{\Lambda}{3},
\]
\[
\sigma'=-3H\sigma-{}^3S+\kappa\pi+[W,\sigma],
\qquad
n'=-Hn+\sigma n+n\sigma+[W,n],
\]
\[
a'=-Ha-\sigma a+Wa.
\]

다음 축약을 정의한다:
\[
E_i(n,X)=\epsilon_{ijk}n_{j\ell}X_{\ell k}.
\]

물질 보존은
\[
\mu'=-3H(\mu+p)+2a\cdot q-\sigma:\pi,
\]
\[
q'=-4Hq-\sigma q+3\pi a+E(n,\pi)+Wq.
\]

SH는 frame 성분의 공간 미분을 제거하지만 spatial covariant divergence를 모두 없애지는 않는다. 특히 \(D_iq^i=-2a_iq^i\)이므로 class B의 에너지식에는 \(+2a\cdot q\)가 남는다.

matter와 radiation은 각각 \((\mu_s,p_s,q_s,\pi_s)\)를 보존하고 geometry에서는 합을 사용한다. 교환항이 있으면 각 sector의 energy/momentum source를 분리하여 기록하고 총합이 0이어야 한다. π_s를 처방 입력으로 받는 background 계는 그 stress 입력에 대해 닫혀 있다. 물리적 radiation π_s의 시간 진화는 별도의 kinetic/transport closure가 제공한다.

## 4. 정확한 defect 전파

다음을 정의한다:
\[
C=3H^2-\sigma^2+\frac{{}^3R}{2}-\kappa\mu-\Lambda,\quad
M=\kappa q-3\sigma a-E(n,\sigma),\quad J=na.
\]

위 자유진화계의 algebraic extension에서

\[
C'=-2HC-2a\cdot M,
\]
\[
M'=(-4HI-\sigma+W)M+
       (3n-\operatorname{tr}n\,I+3A_\times)J,
\]
\[
J'=(-2HI+\sigma+W)J .
\]

Wolfram은 임의 symmetric n, arbitrary a와 STF σ,π에 대해 이 세 식의 잔차를 정확히 0으로 반환했다. 따라서 J≠0일 때 생기는 Codazzi forcing도 포함된다. 물리적 homogeneous geometry는 J=0에서 해석한다.

이 C 정의와 Raychaudhuri 자유진화에 대한 C의 계수는 −2H이다. 현재 conventions.constraint_propagation_matrix의 −3H는 이 식에 그대로 사용할 수 없다. 다른 자유진화 formulation의 constraint addition 여부를 분리해야 한다. 직접 판별 예는 flat vacuum off-shell σ=n=a=μ=Λ=0, H≠0: C=3H², H′=−H²이므로 C′=−2HC다.

## 5. BASS H-normalized 식과 구현 수정

BASS의 τ는 \(d\tau=H\,d\ell\)이며 H≠0에서만 사용한다.
\[
\Sigma=\sigma/H,\quad N=n/H,\quad A=a/H,\quad
\Omega=\kappa\mu/(3H^2),\quad P=\kappa p/(3H^2),
\]
\[
Q=\kappa q/H^2,\qquad\Pi=\kappa\pi/H^2,\qquad
\Omega_\Lambda=\Lambda/(3H^2),\qquad
\Sigma^2=\Sigma:\Sigma/6.
\]

Q와 Π에는 Ω와 같은 3이 분모에 들어가지 않는 혼합 정규화를 지켜야 한다.
\[
q_{\rm dec}=2\Sigma^2+\tfrac12(\Omega+3P)-\Omega_\Lambda.
\]

일반 pressure의 물질식은
\[
\frac{d\Omega}{d\tau}=(2q_{\rm dec}-1)\Omega-3P
+\frac23 A\cdot Q-\frac13\Sigma:\Pi,
\]
\[
\frac{dQ}{d\tau}=(2q_{\rm dec}-2)Q-\Sigma Q+
3\Pi A+E(N,\Pi)+WQ.
\]

비틸트 γ-law \(P=(\gamma-1)\Omega\)에서는
\[
\Omega_{,\tau}=(2q_{\rm dec}+2-3\gamma)\Omega+
\tfrac23 A\cdot Q-\tfrac13\Sigma:\Pi.
\]

기존 구현의 (2q−2)Ω에 필요한 보정은 \((4-3\gamma)\Omega\)이다.
π 또는 flux가 주어졌다는 사실만으로 radiation EOS가 성립하지 않는다.

### 반례와 acceptance checks

1. Flat FLRW dust: Σ=N=A=Q=Π=0, Ω=1, γ=1 → q_dec=1/2. 기존 Ω′=−1, Gauss′=−1; 교정식은 Ω′=0.
2. Flat FLRW radiation: 같은 geometry, γ=4/3 → q_dec=1, 기존·교정식 모두 Ω′=0.
3. Rotating class B: N=0, A=(a,0,0), Σ=diag(s,−s,0), Q=(3as,0,0), R=(0,0,r). geometry의 Codazzi vector가 회전하므로 Q′의 회전항은 (0,3asr,0)이다. 누락하면 구속면에서 Codazzi′_2=3asr가 남는다.
4. Arbitrary normal-frame pressure와 q override: 아래 explicit defect 식으로 일관성을 검증한다.
5. Off-constraint random tests는 J forcing을 포함해 exact polynomial 식과 대조한다. J=0만 강제한 sample로 off-constraint propagation의 전체 범위를 주장하지 않는다.

### q override와 pressure

tilted perfect fluid에서 rest-frame EOS γ가 주어져도 normal-frame \(P=(\gamma-1)\Omega\)는 일반적으로 성립하지 않는다. \(\beta=v/c\), \(G_+=1+(\gamma-1)\beta^2\)일 때

\[
\frac p\mu=\frac{3(\gamma-1)+(3-2\gamma)\beta^2}{3G_+},
\]
\[
Q=\frac{3\gamma\Omega}{G_+}\beta,\qquad
\Pi=\frac{3\gamma\Omega}{G_+}
\left(\beta\beta^{T}-\frac{\beta^2}{3}I\right).
\]

이를 Raychaudhuri 식에 대입하면
\[
q_{\rm dec}=2\Sigma^2+
\frac{(3\gamma-2)+(2-\gamma)\beta^2}{2G_+}\Omega-\Omega_\Lambda.
\]

따라서 API는 일반 matter일 때 P를 명시적으로 받거나, legacy q override로부터
\(P=(2q_{\rm dec}-4\Sigma^2-\Omega+2\Omega_\Lambda)/3\)를 implied pressure로 정의해야 한다. 이 후자의 선택은 Raychaudhuri와의 일관성을 보장하는 pressure 계약이며 별도의 EOS 채택은 별도 입력에 달려 있다.

normalized constraints를
\[
C_G=\Sigma^2+K+\Omega+\Omega_\Lambda-1,\quad
C_D=3\Sigma A+E(N,\Sigma)-Q,\quad J_N=NA
\]
로 두면 임의의 독립 q 입력에 대해
\[
C_{G,\tau}=2q C_G-\tfrac23 A\cdot C_D+
2\left[q-\left(2\Sigma^2+\tfrac12(\Omega+3P)-\Omega_\Lambda\right)\right],
\]
\[
C_{D,\tau}=\left[(2q-2)I-\Sigma+W\right]C_D
-\left[3N-\operatorname{tr}N\,I+3A_\times\right]J_N,
\]
\[
J_{N,\tau}=(2qI+\Sigma+W)J_N.
\]

세 식 모두 exact symbolic 검산을 통과했다. pressure와 q가 불일치하면 위 첫 식의 마지막 항이 남는다.

## 6. H=0을 지나는 고정 scale adapter

proper time t에서 유한한 reference time t_*를 고정한다:
\[
x=t/t_*,\quad h=t_*H_{\rm phys},\quad s=t_*\sigma_{\rm phys},
\quad n_*=ct_*n_{\rm geom},\quad a_*=ct_*a_{\rm geom},
\]
\[
U_s=\frac{8\pi Gt_*^2}{c^2}\mu_s,\quad
P_s=\frac{8\pi Gt_*^2}{c^2}p_s,\quad
Q_s=\frac{8\pi Gt_*^2}{c^2}q_s,\quad
\Pi_s=\frac{8\pi Gt_*^2}{c^2}\pi_s,\quad
L=\Lambda c^2t_*^2 .
\]

이 변수들은 모두 dimensionless이며 x 미분의 ODE는 §3에서 H→h, σ→s, n→n_*, a→a_*, κμ→U, κp→P, κq→Q, κπ→Π, Λ→L로 치환한 형태다. 어떤 RHS도 h로 나누지 않는다. 각 sector가 radiation인지 matter인지는 P_s·Π_s closure에 보존한다.

H-normalized 상태로의 변환은 h≠0에서 \(\Sigma=s/h,\ N=n_*/h,\ A=a_*/h,\ \Omega_s=U_s/(3h^2), Q_s^{(H)}=Q_s/h^2,\Pi_s^{(H)}=\Pi_s/h^2\)다. turnaround에서는 고정 scale 상태를 그대로 적분한다.

## 7. 극한 및 참조값

- Bianchi I: n=a=0 → R3=S3=0. vacuum Kasner \(H=1/(3\ell)\), \(\sigma_i=(p_i-1/3)/\ell\), \(\sum p_i=\sum p_i^2=1\)이 해다.
- Type II: n=diag(n1,0,0),a=0 → R3=−n1²/2, S3=diag(2n1²/3,−n1²/3,−n1²/3).
- Type IX isotropic: n=n0 I,a=0 → R3=3n0²/2, S3=0. FLRW curvature radius b와의 대응은 n0=2/b.
- Type V: n=0 → R3=−6a²,S3=0. Milne은 H=1/ℓ, |a|=1/ℓ, vacuum.
- Type VII_h: n=diag(0,n0,n0),a=(a1,0,0) → S3=0, R3=−6a1²; isotropic open-FLRW limit의 독립 chart 확인.
- de Sitter: n=a=σ=μ=p=0, H²=Λ/3, H′=0.
- Closed dust turnaround, SI 참조: b(η)=B(1−cosη), t(η)=B(η−sinη)/c, H=c sinη/[B(1−cosη)²], n0=2/b, μ=3c⁴/[4πG B²(1−cosη)³]. η=π에서 H=0이고 \(\dot H=-c^2/(8B^2)\)가 유한하다.

## 8. 상태와 남은 구현 의무

이 노트는 유도·원전·exact symbolic / exact rational 검산 산출물이다. main agent가 소스 수정과 실제 runtime regression을 수행한다. 이 하위 작업은 저장소 파일을 변경하지 않았다. 공개용 artifact에는 직접 작성한 노트, WL/Python 검산 코드와 provider receipt를 채택하면 된다. 내려받은 원전 PDF와 렌더는 중간 조사 자료다.

새로운 strong no-go 성과를 주장하지 않는다. 발견한 두 구현 결함의 조건·반례와 최소 교정, pressure 인터페이스에 필요한 선택을 정확히 특정했다.

## 9. 통합·독립 리뷰 후 명확화

위 §1의 SymPy PACKAGE_MISSING은 이론 조사 당시의 관측이다. 후속 격리 환경에는
SymPy 1.14.0을 설치했고, Python·C++ 실행 및 첨부 Rust 1.94.1 복구·빌드를 실제
완료했다. Wolfram exact symbolic 검산 자체는 변경되지 않았다.

§4의 기존 `conventions.constraint_propagation_matrix`를 결함으로 분류하지 않는다.
독립 리뷰가 `tests/test_rotation_sign.py`와 실제 호출 관계를 확인한 결과, 그
helper는 공간 ij-Einstein 자유진화의 propagation을 나타낸다. 새 core는
Raychaudhuri 자유진화를 사용한다. 두 formulation의 H 미분 차이가 −C/6이면
C 미분의 차이는 6H(−C/6)=−HC여서 −3HC와 −2HC가 정확히 연결된다. 구속면에서는
같은 물리계이며, off-constraint extension이 다르다. 새 core는 이 legacy helper를
호출하지 않는다.

양의 antipodal stream 대조군에서 `isotropic`은 stress-energy의 2차 모멘트가
등방적이라는 뜻이다. 여섯 방향으로 구성된 이산 분포 전체의 SO(3) 등방성을
주장하지 않는다. 제약을 소거한 5변수 reference는 진화 경로와 종속변수 처리가
독립적이지만 stream moment 함수는 공유한다. 따라서 별도의 moment 구현과의
완전한 독립 교차 검증으로 세지 않는다.
