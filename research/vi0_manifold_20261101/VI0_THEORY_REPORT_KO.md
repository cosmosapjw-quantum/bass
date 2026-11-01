# BASS G-DYN-MANIFOLD-VI0 | 첫 구성적 이론 단위 (2026-11-01)

## 0. 판정과 계보

**이론 결과:** `DERIVED_EXACT_SCOPED`, 두 CAS의 유리수 witness에서 Kato·projector 항등식 확인, 64개 실수 물리 상태 numerical spot check, 9/9 local pytest PASS. **원래 G-DYN-MANIFOLD-VI0 전체 게이트는 PARTIAL**, `P-MIG-II-PREFLIGHT=OPEN`, Join J1=HOLD, production/merge 권한 없음. 새 Einstein/Kato Rust IVP=0. `native_subagent: NOT_RUN` (이번 호스트에 native spawn 없음); 연결된 Remote Desktop Commander 기기 `cosmosapjw`는 이 실행 시 OFFLINE이며 로컬 원래 작업 트리를 검사/수정하지 않았다.

BASS `main` 기준 정확한 commit `9c6506e4e2087129a8b674ff10438e5db1a55c9d`; 원래 8월 계획은 PR #15 `af467a974cfd9bd8ccd59870e5a03c8099f23db1`, scalar Type-II 원전 PR #5–#7. BASS 공식 Python source blobs 및 원래 Type-II scalar Kato projectors는 별첨 `VI0_SOURCE_AUTHORITY.json`과 소스 코드 `SOURCE_SHA`에 정확한 Git blob SHA-1로 고정한다. PR #15는 design-only이므로 결과를 이미 달성했다고 오기하지 않는다.

문헌 기준: S. Hervik, “The asymptotic behaviour of tilted Bianchi type VI0 universes”, *Classical and Quantum Gravity* **21** (2004), 2301–2317, DOI `10.1088/0264-9381/21/9/007`, [arXiv:gr-qc/0403040](https://arxiv.org/abs/gr-qc/0403040), §2.1 및 표 1: 단일 tilted γ-law VI0 전체 상태공간 7차원, 비틸트 하위공간 4차원. 기존 문헌의 7차원 결과를 새로운 발견으로 주장하지 않는다. 이번 추가 구성은 **BASS 자신의 소스·scalar projector·Kato interface에 맞는 국소 좌표와 정확한 rank 증명**이다.

## 1. 정의, 컨벤션 및 유효범위

- 시공간 부호 `(-,+,+,+)`, `ε123=+1`; BASS Hubble-정규화 `N=n/H`, `Σ=σ/H`, `Ω=ρ_n/(3H²)`와 코드 내부 단위 `c=8πG=1`을 따른다. 물리 단위를 복원하면 관련 원 상수를 유지해야 한다.
- 단일 γ-law 완전유체 `p_rest=(γ-1)ρ_rest`, `0<γ<2`. 원래 BASS `bianchi/matter/fluid.py`의 `q_flux^a=3γ Ω v^a/G_+`, `G_+=1+(γ-1)v²`, `v²<1`을 그대로 쓴다.
- Class A VI₀ 고유프레임: `A_a=0`, `N=diag(0,p,-q)`, `p>0, q>0`; 세 고윳값은 서로 달라 연속 회전 안정자가 없고 고유프레임은 부호 등 이산 자유도만 남는다.
- `Σ11=-2Σ+`, `Σ22=Σ++sqrt(3)Σ-`, `Σ33=Σ+-sqrt(3)Σ-`; `Σij=Σji`는 이 행렬의 **원시 성분**으로, Hervik의 `sqrt(3)`로 재정규화한 비대각 `Σ12` 등과 혼동하면 안 된다.
- `Ω*>0`, `Ω>0`인 비진공 내부. Thomson scalar equilibrium의 bulk velocity가 이 완전유체의 `v_a`와 **동일하다**는 것은 물리 모델 결합 가정이다. 독립 전자 bath나 편광과 자동으로 동일하지 않다.

## 2. Codazzi의 정확한 소거

원래 BASS 함수 `codazzi_residual`은

\[
 C^a=\epsilon^{abc}N_{bd}\Sigma_c{}^d-Q^a,
 \qquad Q_a=\frac{3\gamma\Omega}{G_+}v_a.
\]

대각 `N=(0,p,-q)`이면 순서 `(23,13,12)`의 비대각 shear에 대한 Codazzi 방정식은

\[
\begin{aligned}
(p+q)\Sigma_{23}&=3\gamma\Omega v_1/G_+,\\
-q\Sigma_{13}&=3\gamma\Omega v_2/G_+,\\
-p\Sigma_{12}&=3\gamma\Omega v_3/G_+.
\end{aligned}
\]

여기서 세 계수 `p+q, -q, -p`가 모두 0이 아니므로 어떤 실수 tilt 방향도 하나의 불필요한 축으로 강제되지 않는다. 따라서 세 비대각 shear는 `Ω,v,p,q,γ`로 **정확히** 소거된다.

## 3. Gauss 축약, 양의 해, exact rank

BASS의 `Σ²=(tr Σ²)/6`, `K=(p+q)²/12` 및 Gauss `Σ²+K+Ω=1`을 사용한다. `D=(p+q,-q,-p)`, `f=3γ/G_+`라 놓으면 `Σoff_i=f Ω v_i/D_i`. 그러므로

\[
\begin{aligned}
 \Omega +\beta\Omega^2&=\Omega_*,\\
 \Omega_*&=1-\Sigma_+^2-\Sigma_-^2-\frac{(p+q)^2}{12},\\
 \beta&=\frac{3\gamma^2}{G_+^2}\left(\frac{v_1^2}{(p+q)^2}+\frac{v_2^2}{q^2}+\frac{v_3^2}{p^2}\right)\ge0.
\end{aligned}
\]

`Ω*>0`에서 양의 해는 유일하고 cancellation-free 형태

\[
\boxed{\Omega=\frac{2\Omega_*}{1+\sqrt{1+4\beta\Omega_*}}}
\]

를 갖는다. `(Σ+,Σ-,p,q,v1,v2,v3)`는 이 열린 영역에서 7개의 매끄러운 독립 국소 좌표다. 전체 11개 변수(대각 shear 2, 비대각 3, N 2, tilt 3, Ω 1)의 4개 제약을 푼다는 주장과 동치다.

정확한 4×4 constraint Jacobian의 열을 `(Σ23,Σ13,Σ12,Ω)`로 잡으면, 제약면 위에서

\[
\det J_C=pq(p+q)(1+2\beta\Omega)>0.
\]

이는 Schur 보수로 직접 유도했고 SymPy와 Wolfram의 독립 symbolic residual이 **0**이다. 따라서 단순한 수치 SVD 결과가 아니라 열린 VI₀ 내부에서 참인 exact rank-4 증명이다. `p→0` 또는 `q→0`이면 이 좌표계/선택 minor가 퇴화하며, 그 경계는 Type-II 등 별도 branch로 재분류해야 한다.

## 4. 원본 Type-II scalar Boltzmann 이동 평형을 VI₀로 일반화

BASS `generated/rust/typeii/typeii_kato.rs` 및 `compiler/validation/typeii_conservation_quad.py`의 scalar bolometric 정의를 **같은 고유프레임에 고정된** 관측 각도구적으로 확장한다:

\[
 D_\alpha=\Gamma(1-\mathbf v\cdot\mathbf n_\alpha),\quad
 r_\alpha=D_\alpha^{-4},\quad
 a_\alpha=\frac{w_\alpha}{4\pi}(1-\mathbf v\cdot\mathbf n_\alpha),\quad
 P=\frac{r a^{\mathsf T}}{a^{\mathsf T}r}.
\]

`0≤|v|<1`, 모든 활성 `w_α>0`에서 `d=a^T r>0`. 항상 `P²=P`이고 rank(P)=1이다. 하지만 **projector 가족의 매개변수 rank는 1이 아니라 3**이라는 구분이 중요하다. 여섯 축 방향 `±e_i`가 존재하는 각도구적에서는

\[
\frac{P_{+i,\alpha}}{P_{-i,\alpha}}=
\frac{r_{+i}}{r_{-i}}=\left(\frac{1+v_i}{1-v_i}\right)^4,
\quad
\partial_{v_j}\log\frac{r_{+i}}{r_{-i}}=\frac{8\delta_{ij}}{1-v_i^2}.
\]

세 좌표가 전역적으로 복구 가능하고 접선 rank는 3이다. 원본 Type-II 단일 `P(v2)`만 VI₀에 대입하면 `v1`, `v3`에 대한 실제 projector 변동을 잃는다. 실제 BASS Lebedev-26 구적은 이 축을 포함한다. 다른 일반 구적은 독립 방향 Gram을 별도로 증명해야 한다.

미분 계산:

\[
\begin{aligned}
 r_{\alpha,i}&=4r_\alpha\left[\frac{n_{\alpha i}}{1-v\cdot n_\alpha}-\Gamma^2 v_i\right],\\
 a_{\alpha,i}&=-w_\alpha n_{\alpha i}/(4\pi),\\
 P_{,i}&=\frac{r_{,i}a^T+ra_{,i}^T}{d}-P\frac{d_{,i}}d,\\
 \dot P&=\dot v_i P_{,i},\quad K=[\dot P,P],\quad [K,P]=\dot P.
\end{aligned}
\]

마지막 두 식은 정확한 projector 미분 항등식으로부터 따른다. **이것은 각도구적과 ray-label이 VI₀ 고유프레임에 함께 고정된 표현에서만** `\dot P=\dot v^i P_{,i}`라고 쓰는 계약이다. 일반 Fermi/angular moving grid에서는 `\dot n`·weight·frame screen 추가 항을 별도로 운반해야 한다.

## 5. 진화 중 VI₀ 고유프레임 유지의 필요 회전

BASS의 `general` 차트는 `Ndot=q_dec N+ΣN+NΣ+[W,N]`을 쓴다. `N=diag(0,p,-q)`를 비대각 shear가 있어도 계속 대각 상태로 유지하려면

\[
 W_{ij}=-\frac{n_i+n_j}{n_j-n_i}\Sigma_{ij},\quad
 W_{12}=-\Sigma_{12},\quad W_{13}=-\Sigma_{13},\quad
 W_{23}=\frac{p-q}{p+q}\Sigma_{23}.
\]

이는 exact rational witness에서 세 off-diagonal `Ndot`가 0인 것으로 검증했다. `p,q>0`에서 분모는 사라지지 않는다. 사용자가 실제 속도 진화를 연결하려면 `v'_a` 안에 BASS 채택 `COMMUTATOR` 프레임 회전 부호를 포함해야 한다. 이 단계에서 그 동역학 전체를 구현/증명했다고 간주하지 않는다.

## 6. 분기·반례 및 검증 경계

| 분기 | 기하·물리 상태공간 | scalar projector 가족 |
|---|---|---|
| generic VI₀, `p,q>0,Ω>0,|v|<1` | 국소 7차원 | 고유프레임의 3 tilt 좌표 필수 |
| strict non-tilted `v=0` | 4차원 invariant branch | 그 branch 위 변화 rank0; full 7D tangent에서 v 방향 미분 rank3 |
| `p=0` 또는 `q=0` | Type-II 경계, 이 좌표계 Jacobian minor 퇴화 | 별도 경계 분류 필요; `P(v2)` 직접 이식 금지 |
| `Ω=0` | vacuum, 유체 tilt의 물리적 의미 소멸 | 충돌 bath 없는 경우 scalar projector가 물리적 상태가 아님 |
| `γ=6/5` | Hervik의 동역학적 안정성 bifurcation | **이 7D algebraic rank는 유지**. 안정성 변화와 구속 rank 혼동 금지 |
| `|v|→1` 또는 퇴화된 격자 | 경계·특이 조건 | 현재 미분·Kato 계약의 유효범위 밖 |

**검산 실적:** SymPy 원 식의 Codazzi3, Gauss, Schur determinant identity exact; 6-axis rational projector `P²-P=0`, `d(P²)-dP=0`, `[[Pdot,P],P]-Pdot=0`; 독립 Wolfram은 constraint `{0,0,{0,0,0}}`, projector `{0,0,0,3,{0,0,0}}`; Python 9/9 테스트 PASS와 64 seeded 물리 상태의 구속·idempotence residual 10^-15 수준. Type-II `P(v2)` 가짜 양성, Codazzi 하나 생략, constraint boundary, 잘못된 zero-tilt rank를 부정 검사로 차단한다. 계산 경로는 **동일 저자+별도 CAS**이며 별도 사람 심사와 생산 Rust 편입은 `NOT_RUN`이다.

## 7. 다음 진짜 선행 의무

- VI₀ production classifier FULL PASS로 승격하려면 **실제 VI₀ 진화 방정식에서 7D constraint의 전파**, 공변 frame/angular remap, scalar collision operator의 정확한 동일성, 추가 대칭·표본 경계 branch, 기호 표기와 실 구현의 호환성을 완성해야 한다. 현재는 그 중 하나인 국소 exact constraint/projector 이론이 완료된 것이다.
- 병렬 `P-MIG-II-PREFLIGHT`는 아직 별도 OPEN: Type-II 5-state host adapter, crate-root offline reproducibility, scalar uniformization과 old-AEM2/Kato-AEM2 비교 계약. Rust production은 건드리지 않는다.
- Join J1과 production migration은 여전히 HOLD. BASS 연구 상위 15노드의 기존 9/15 scoped/source-mapped와도 분모가 다르므로 과학적 진행률을 혼합하지 않는다.

**Stop after this one bounded theory unit; no automatic next auxiliary PR, no merge, no production.**
