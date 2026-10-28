# BASS CE1-F 연구보고서: 양의 불연속 angular table의 MPFR 구적오차와 Einstein–Vlasov 전달

## 1. 상태·원본·계산 경계

본 단위 CE1-F는 **COMPLETE_SCOPED_TABULATED_CELL_SOURCE**, 상위 CE-1은 **PARTIAL**, 원래 15개 상위 DAG는 **9/15**이다. 독립 코드 브랜치 `research/bass-ce1f-tabulated-meanray-implementation-20261029`, 부모 C4 commit `a3ddc5ed49d245e87fe393ec17e889dbc77f540d`, 물리적 전제/이론은 `research/ce1f_20261029/THEORY.md`와 `ALGORITHM.md`를 사용했다. 상위 CE1-E PR237/commit `a05906527d7dd5e5f6a653a0e4f7d977679d4a0c`와 immutable ZIP SHA256 `9105b9ef9dd0494bbb520085b9246bd0cb2e40ce1a6c92b9a776dd260f2a34e2`는 변경하지 않았다. 초기의 다른 band-Fourier 대안은 원격 정본으로 게시하지 않고 C4 원형을 채택했다.

현재 Python3.13.5, NumPy2.3.5, SciPy1.17.0, GNU MPFR6 실행 환경이 검증됐다. 부모 회귀테스트39, 신규8을 로컬에서 통과했다. 원본 선행 과학 캠페인 재실행0, 신규 CE1-F coupled IVP4, 원본-cell 독립 source 대조16, 결정론적 stress36, 이력 단위 에너지 derivative3×3. 외부 Wolfram에서 centered Taylor f_i''와 주장한 수식 차가 정확히 0임을 확인했다. native subagent tools 이 세션에 노출되지 않아 `NOT_RUN_TOOL_NOT_EXPOSED`; 독립 공식 소프트웨어 검증 아님. 첫 RED는 8개 NotImplementedError, GREEN 전에 정확 유리수와 binary64 비교를 잘못한 테스트 하나를 수정했다. 수학적 허용오차나 solver RHS는 그때 변경하지 않았다.

## 2. 정확한 angular table의 물리 의미

Spatially homogeneous diagonal Bianchi-I, metric signature \((-+++ )\), normal proper \(u=t/T_*\), \(\ell_i=\log a_i\), \(h_i=T_*H_i\), \(\Lambda=0\), 질량0/무충돌 photon radiation, 좌표축의 모든 반사에 대해 짝대칭이다. \(E,P=(8\pi G T_*^2/c^2)\)× 물리 에너지밀도·압력이다.

\(\mu=|q_z|\in[0,1]\), \(t=2\phi/\pi\in[0,1]\)의 첫 octant를 정확 유리수 edge로 나누고, 각 cell의 **반사된 8개 patch를 모두 합친 에너지** \(w_C\ge0\)를 입력한다. 각 patch 내부 각도 energy density를 \(F_0=w_C/[8\Delta\mu\Delta\phi]\)로 정확히 정의한다. 그러므로 참 연속 초기 에너지는 \(E(0)=\sum_C w_C\)이고, 경계 점프는 실제 초기자료의 일부이다. \(w_C\)를 면적비대로 정수 세분화해도 연속 \(F_0\)는 그대로다. 이것은 점값만 주어진 실제 하늘지도에 보간/정칙성을 자동 가정하는 인증이 아니다.

\(b_i=e^{-2\ell_i}\), \(V=e^{\sum\ell_i}\), \(x_i=q_i^2\)를 쓰면 \(\sum_i x_i=1\)이고
\[
E(\ell)=V^{-1}\sum_C w_C\left\langle\sqrt{b\cdot x}\right\rangle_C,\qquad
P_i(\ell)=V^{-1}\sum_C w_C\left\langle\frac{b_ix_i}{\sqrt{b\cdot x}}\right\rangle_C.
\]

실제 방정식은 \(\ell_i'=h_i\), \(h_i'=-\theta h_i+P_i(\ell)\)이고 \(\theta=\sum h_i\). 물리계에 angular multipole truncation은 없고 충돌/tilt/공간 feedback은 포함되지 않는다.

## 3. 정확 평균 ray와 2차 cell 오차 정리

\(m_C=\langle x\rangle_C\)의 각 성분은 정확 μ band 적분과 방향지정 MPFR \(\sin,\cos\) 끝점으로 계산된다. 특히 \(m_z=(\mu_a^2+\mu_a\mu_b+\mu_b^2)/3\)이고 \(m_x=(1-m_z)c\), \(m_y=(1-m_z)(1-c)\), \(c=1/2+[\sin 2\phi_b-\sin 2\phi_a]/[4(\phi_b-\phi_a)]\)이다. 구적 ray는 \(n_{C,i}=\sqrt{m_{C,i}}\)를 binary64로 저장한다. 각도 중앙점 ray \(q(\mu_{mid},\phi_{mid})\)와 다르며, 전자의 정확 평균 조건 때문에 isotropic geometry에서 일차 오차가 사라진다.

\(0\le\ell_i\le L\), \(r_{min}=e^{-L}\), \(d=1-e^{-2L}\), \(x_i\in[l_i,u_i]\), \(s_i=u_i-l_i\), \(V_C=\sum_i s_i^2/4\), \(Q_C=3d^2V_C/4\)라 두자. \(f_i(x)=b_ix_i/\sqrt{b\cdot x}\), \(\Delta=x-m_C\)에서
\[
f_i''(t)=-\frac{b_i\Delta_i(b\cdot\Delta)}{(b\cdot x(t))^{3/2}}+\frac{3b_ix_i(t)(b\cdot\Delta)^2}{4(b\cdot x(t))^{5/2}},\quad x(t)=m_C+t\Delta .
\]
\(\langle\Delta_i\rangle_C=0\), Popoviciu \(\langle\Delta_i^2\rangle\le s_i^2/4\), 그리고 \(\langle(b\cdot\Delta)^2\rangle\le Q_C\)로부터
\[
\boxed{\big|\langle f_i\rangle_C-f_i(m_C)\big|\le \frac{s_i\sqrt{Q_C}}{4r_{min}^3}+\frac{3u_iQ_C}{8r_{min}^5}.}
\]
이는 점프를 가로질러 미분한 결과가 아니다. **각 cell 안의 기하학 kernel**에만 Taylor 정리를 적용했다.

저장된 실제 binary ray는 \(X_i=n_{C,i}^2\)이며 \(X_i=m_i\)를 가정하지 않는다. \(\epsilon_i\ge|X_i-m_i|\), \(\epsilon_1=\sum\epsilon_i\), \(r_0=e^{-L}\sqrt{\min(1,\sum X_i)}\), \(M_i=\max(u_i,X_i)\)이면
\[
|f_i(m)-f_i(X)|\le \epsilon_i/r_0+M_i\epsilon_1/(2r_0^3).
\]
추가로 실수인 정확 energy mass \(w_C\)와 저장된 float mass \(\hat w_C\) 차이는 \(|w_C-\hat w_C|\sqrt{\sum X_i}\) 이하이다. 세 항 모두 **MPFR192 RNDD/RNDU 외향 구간**으로 합하고 어떤 수정·재정규화도 하지 않는다.

## 4. 초기 제약과 기하학 error transfer

연속 \(E_0=\sum w_C\)는 정확 유리수. 별도로 저장된 \(E_{0,Q}=\mathrm{float64}\left(\sum\hat w_C\sqrt{\sum X_i}\right)\)와의 차이를 MPFR로 감싸고, 연속 초기 shear는 저장된 sx,sy의 **정확 이진수**, \(s_z=-(s_x+s_y)\)로 정의한다. \(h_i(0)=\sqrt{[E_0+\sum s_i^2/2]/3}+s_i\)와 실제 저장된 초기 h 차이도 감싼다.

전 방향 초기 팽창과 \(E_0>0\)이면 \(h_i\ge0\), \(E'=-\sum_i h_i(E+P_i)\le0\), \(h_i'\le E_{max}\)를 사용해 두 해를 포함하는 \(\ell\)-box를 구성한다. \(\eta_Q\)를 위 pressure discrepancy uniform bound, \(d_0\)를 초기 h 차이라고 하면
\[
D^+e_{\ell}\le e_h,\qquad D^+e_h\le4E_{max}e_{\ell}+\eta_Q,\qquad (e_{\ell}(0),e_h(0))=(0,d_0).
\]
`certified_tabulated_geometry`는 이 양의 비교계를 MPFR로 전파한다. 이것은 **두 정확한 실수 ODE**의 차이 상계이며, 내부에서 사용한 NumPy/SciPy float64 numerical integration의 누적 오차까지 인증한 값이 아니다.

## 5. 실제 캠페인: 독립 원본-cell 구적과 이산 refinement

입력: μ edges `(0,0.5,1)`, 첫 octant φ/(π/2) edges `(0,1/3,2/3,1)`, 실제 총 cell energies `((.09,.15,.06),(.20,.12,.18))`, 합 \(E_0=4/5\). 각 원본 cell에서 독립 40×40 Gauss 적분(평균 ray/certificate 함수를 호출하지 않음)을 사용했다. \(0\le\ell_i\le0.075\), \(0\le u\le0.08\)의 출력을 표로 묶는다.

| 원본 cell 선형 refinement | 저장 ray 수 | source uniform 상계 | geometry h 상계 | refine8 IVP 대비 실측 끝점 h 차이 |
|---:|---:|---:|---:|---:|
| 1 | 6 | 0.0098787606608 | 0.00060725883341 | 1.0229410363e-05 |
| 2 | 24 | 0.0025361351479 | 0.00015652221196 | 2.5338046927e-06 |
| 4 | 96 | 0.00063375349006 | 3.9204646091e-05 | 5.1191579509e-07 |
| 8 | 384 | 0.00015788079547 | 9.7786871374e-06 | 0 |


지오메트리 상계는 u≤.08의 확장영역 입력 범위를 자동 계산해 전파한 결과다. IVP 차이는 같은 DOP853 설정의 **수치 참조**이며 연속 정확해라고 선언하지 않았다. 초기/동역학적 제약 \(|C|\)의 최대 float64 잔차는 `1.382228e-13` (무차원). 원본 cell 독립 구적 16개와 deterministic stress `36`개 모두 상계 내부이고, stress gap/upper 최대 `0.12863388`, finite-difference 에너지 미분항등식 잔차 `6.7267247e-11`였다. 더 큰 refinement의 bound가 작은 이유는 연속 F0가 바뀌어서가 아니라 cell 안의 variance 및 저장 mean-ray error가 감소했기 때문이다.

등방 full-octant 반례/변형검사: 정확한 \(\langle q_z^2angle=1/3\)인데 geometric midpoint의 \(q_z^2=1/4\)이다. 이 경우 centroid 2차 상계는 0이므로 geometric-midpoint 구적을 그 상계와 섞으면 거짓 PASS가 발생한다. 구현과 테스트는 centroid ray를 사용해 이를 방지한다.

## 6. 분리된 검증, 미완료 의무, 판정

신규 source/test 함수는 기존 `einstein_error_budget.py`, `einstein_interval.py`, `einstein_input_enclosure.py`, `einstein_exponential_source.py`를 수정하지 않는 **additive opt-in Python-oracle** 경로다. 신규 8개와 부모 39개, 총 47개 pytest PASS. 현재 구현 GitHub Actions의 scoped test 및 installed-wheel numerical smoke 결과는 실행된 workflow receipt로 구별한다. S0/S1/S2 Git/Drive/Dropbox create-only로 보존하고 검증 시 차이를 표시한다.

이 단위의 과학 범위는 **정확히 지정된 양의 첫 octant 조각상수 angular table**이다. 점별 표본만 제공된 미지의 연속 sky, 회전·tilt가 있는 비대각 stress, 비균질 Einstein constraints, 충돌 주파수 효과, native Rust, full-range time-integrator certificate, formal MPFR/Python proof와 전체 production solver는 인증하지 않는다. 기존 sibling CE1-F R/C4는 독립 참조로 보존되고 이 구현 branch와 자동 merge하지 않는다.

**CE1-F=COMPLETE_SCOPED_CELL_SOURCE_SECOND_ORDER**, 상위 CE-1=PARTIAL, 상위 DAG=**9/15**, production_ready=false, merge_ready=false. 다음 후보는 CE1-G에서 이 제한된 source의 실제 시간적분 defect를 독립 인증하거나 일반 관측 테이블에 대한 추가 regularity envelope를 명시하는 작업 중 하나이다. 아직 실행하지 않는다.
