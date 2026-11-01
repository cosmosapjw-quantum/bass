# BASS VI0 R1–R10 이론 연구 | Exact constraint propagation and covariant scalar Kato frame lift

**날짜:** 2026-11-01 KST. **원본:** `cosmosapjw-quantum/bass`, 이전 정확한 과학 PR #310 HEAD `71adfbb2948f6c23725a01dfc048e90623a9eab5`, PR #310의 원시 수식 main SHA `9c6506e4e2087129a8b674ff10438e5db1a55c9d`. 이전 PR #15는 2026-08-21 설계 선언이며 현재 production 승격은 하지 않았다. 사용자가 선택한 BASS Type-II/VI0 원래 임계경로의 **다음 실제 이론 의무 한 개**만 수행했다.

**결론:** `DERIVED_EXACT_CLASS_A_CONSTRAINT_PROPAGATION + NUMERICALLY_CHECKED_SCOPED_VI0_DYNAMICS + DERIVED_PURE_GAUGE_SCALAR_PROJECTOR_LIFT`. 원래 `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`, Join J1=`0/2 PASS`, production=HOLD. 다른 연구 방향의 BASS upper 15-node 그래프는 **9/15 scoped/source-mapped 그대로**, 신규 완전 완료 상위 노드 **0**. Native subagent는 사용자 지시에 따라 NOT_RUN, same-author hostile referee만 시행.

## R1–R3: Authority, metric, state, valid domain

- Metric `(-,+,+,+)`, epsilon123=+1, BASS의 **Hubble-normalized prime time**와 내부 c=8πG=1을 명시적으로 인용한다. 이 소스의 무차원 정규화를 외부 시공간의 물리적 단위와 혼동하지 않는다.
- 하나의 tilted gamma-law 완전유체: `p_rest=(gamma-1)rho_rest`, `0<gamma<2`; `Q_a=3 gamma Omega v_a/Gplus`, `Pi_ab=(3 gamma Omega/Gplus)(v_a v_b-v² delta_ab/3)`, `Gplus=1+(gamma-1)v²`.
- 이전 PR310 국소 차트 `(Sigma_plus,Sigma_minus,p,r,v1,v2,v3)` 및 `N=diag(0,p,-r)`를 정확히 재사용한다. `p,r>0`, `Omega_star>0`, `Omega>0`, `v²<1`. 비대각 shear 세 성분과 Ω는 원래 Codazzi·Gauss의 정확한 해로 복원한다. 곡률은 `K=tr(N²)/6-(tr N)²/12`, shear magnitude는 `Sigma²=tr(Sigma²)/6`.
- 1차 문헌: S. Hervik, *The Asymptotic Behaviour of Tilted Bianchi type VI0 Universes*, *Class. Quantum Grav.* **21** (2004) 2301–2317, https://doi.org/10.1088/0264-9381/21/9/007, https://arxiv.org/abs/gr-qc/0403040. 원문의 비대각 `N` 게이지와 현재 **고유값 대각** 게이지는 서로 다른 축 표현이다. 문헌의 7D 전체 공간 자체를 새 발견으로 주장하지 않는다.
- 원래 BASS SSOT: `bianchi/charts/general.py`, `bianchi/matter/fluid.py`, `bianchi/conventions.py`, `generated/rust/typeii/typeii_kato.rs`, 기타 세 파일 포함 총 7개 Git blob SHA는 `vi0_dynamics.py:ORIGINAL_BLOBS`에 고정한다. 원본 변경 금지.

## R4–R5: 정확한 미분 항등식과 구속면 보존 정리

다음은 BASS 저장소의 원래 모델을 재구성한, 방정식 수준에서의 직접 유도다. `q_dec`은 감속변수이며 VI0 음의 곡률 고윳값 `-r`과 전혀 다른 기호다.

`S3=[2N²-(tr N)N]^TF`, `W^T=-W`라고 하면, 원본 기하 RHS는

```
Sigma'=(q_dec-2)Sigma-S3+Pi+[W,Sigma],
N'=q_dec N+Sigma N+N Sigma+[W,N].
```

`J_a=epsilon_abc N_bd Sigma_cd`를 정의하면, 임의의 대칭 N, 무자취 대칭 Sigma와 Pi, 반대칭 W에 대해

```
J'=(2q_dec-2)J-Sigma J+epsilon(N,Pi)+W J
```

가 정확한 다항식 항등식으로 성립한다. 여기서 `epsilon(N,Pi)_a=epsilon_abc N_bd Pi_cd`. 필요한 보조항은 `epsilon(N,S3)=0` (`N`과 `S3`가 교환), `epsilon(Sigma N Sigma)=0` (`Sigma N Sigma` 대칭), `epsilon(N Sigma²)=-Sigma epsilon(N,Sigma)` (3차원 무자취성)이다.

원본 유체 RHS에서는

```
v'=T v-Sigma v+W v-v×(Nv),
T=[(3gamma-4)(1-v²)+(2-gamma) Sigma_ab v_a v_b]/Gminus,
Gminus=1-(gamma-1)v².
```

`Q=3gamma Omega v/Gplus`의 미분에 이 식과 원래 `Omega'`를 대입하면

```
Q'=(2q_dec-2)Q-Sigma Q+epsilon(N,Pi)+W Q
```

가 정확히 성립한다. 물질 미분의 비자명한 스칼라 계수는 **SymPy와 별도 Wolfram**에서 잔차 0으로 소거했다. 따라서 `C=J-Q`에 대한 구속 전파는

\[
\boxed{\mathbf C'=\big[(2q_{\rm dec}-2)I-\Sigma+W\big]\mathbf C.}
\]

또한 `K'=2q_dec K+(1/3)Sigma:S3`이고, `Sigma²'=-2(2-q_dec)Sigma²-(1/3)Sigma:S3+(1/3)Sigma:Pi`이다. 원래 `Omega'`와 `q_dec`의 관계를 사용하면

\[
\boxed{C_G'=2q_{\rm dec} C_G},\qquad C_G=\Omega+\Sigma^2+K-1.
\]

**따름정리:** 규칙적인 한 시간구간에서 정확한 초기 구속 `C_G=C=0`은 연속 ODE 흐름에 의해 보존된다. 이 증명은 전체 class-A 텐서식에 관해 성립하므로 VI0 고유프레임에서는 자동으로 성립한다. 그러나 서로 다른 상호작용 물질, 외부 처방된 Q·Pi, 일반 class B 또는 polarized source closure까지 확장한 정리는 아니다.

## R5: 실제 7차원 VI0 source-owned RHS와 물리 데이터

Distinct VI0 curvature eigenvalues `(0,p,-r)`의 offdiagonal 시간미분을 0으로 유지하는 유일한 국소 회전은

\[
 W_{ij}=-\frac{n_i+n_j}{n_j-n_i}\Sigma_{ij},\quad(i\ne j),
 \qquad W_{12}=-\Sigma_{12},\quad W_{13}=-\Sigma_{13},\quad
 W_{23}=\frac{p-r}{p+r}\Sigma_{23}.
\]

고유값 대각인 `N`과 정확히 slaved `Omega,Sigma_off`를 재구성한 뒤, 전체 기하와 유체 RHS의 `Sigma'_diag,N'_diag,v'`를 7개 좌표 RHS로 직접 읽어낸다. `N'`의 비대각 원소는 정확하게 0이고, 전구속 차트 미분 `D X(z) f_7(z)`과 전체 `F(X(z))`의 차이는 복소단계 미분으로 검산했다.

**실제 실행:** deterministic 12개의 양의 VI0 gamma-law 초기조건, `gamma=1, 1.1, 4/3, 1.65` 각 3개, Hubble-normalized time `0 ≤ u ≤ 0.2`, 41 저장 시점, SciPy DOP853 `rtol=2e-11,atol=2e-13`. **새로 계산한 모형 물리 상태 492행** (`VI0_DYNAMIC_PHYSICAL_HISTORIES.csv`). 초기형은 새로 계산한 완전유체 Bianchi VI0 IVP이지 관측 데이터나 Bianchi 광자 Boltzmann 해가 아니다.

| 대상 | 전 492 상태의 최대 절대 잔차 |
|---|---:|
| Gauss `C_G` | `4.440892098500626e-16` |
| Codazzi `C` | `1.1102230246251565e-16` |
| DC·F와 정확한 구속 전파식, 7D 차트 미분과 full RHS | `8.881784197001252e-16` |

## R5–R6: 프레임 회전과 scalar Kato의 진짜 gauge 경계

원래 Type-II scalar collision projector `P=r a^T/(a^T r)`에서 각도로 주어진 광선 n와 유체속도 v에 대하여

```
r_alpha=(1-v²)^2/(1-v·n_alpha)^4,
a_alpha=w_alpha(1-v·n_alpha)/(4pi).
```

각도 grid가 시간에 따라 움직인다면 반드시 전체 체인룰을 써야 한다:

\[
\dot P=\sum_i\dot v_i\partial_{v_i}P+
\sum_{\alpha j}\dot n_{\alpha j}\partial_{n_{\alpha j}}P+
\sum_\alpha\dot w_\alpha\partial_{w_\alpha}P.
\]

`v'_W=Wv`, `n'_W=Wn`, `w'_W=0`이고 `W` 반대칭이면 순수 gauge 기여는 `d(v²)=d(v·n)=0`이므로 **`(P')_W=0`**. 실제 광선 방향의 물리적 Liouville drift, angle-weight remap과 편광 screen rotation은 이 항과 **다른** 독립 연산이며 아직 계산하지 않았다. `K=[P',P]`의 관계 `[K,P]=P'`는 그대로 성립한다.

**적대적 반례:** `n'`을 0으로 고정하고 `v'=Wv`만 쓰면 최대 가짜 `|P'|=0.13493534547916913`이 발생한다. 실제 동시 회전에서는 `3.851859888774472e-34`. `Wv`를 유체 ODE에서 누락하면 Codazzi derivative mismatch `0.25076676381833124`; `epsilon(v,Nv)`를 누락하면 `0.017398259170237906`이 된다.

**더 중요한 claim 경계:** `P`는 rank-one **oblique** projector다. 물리 witness에서 `max|P-P^T|=0.20565940148803666`, `max|K+K^T|=0.13738641065917678`. 그러므로 일반 Hermitian orthogonal spectral projector에서 따라오는 **unitary Kato** 논증을 여기로 무단 이식하면 안 된다. 현재 인정되는 것은 projector subspace intertwinement뿐이다.

## R6–R7: 검증 등급과 실제 반증 통제

- 임의 class-A 대칭 N, STF Sigma 및 Pi, 반대칭 W의 미분 항등식 3개와 곡률 항등식은 SymPy **정확한 다항식 잔차 0**.
- Wolfram도 별도 유리수 VI0 텐서 witness에서 momentum residual `{0,0,0}`, eigenframe offdiagonal N' residual `{0,0,0}`, K' curvature residual `0`을 반환했다. 유체 Qdot의 일반 scalar 식도 Wolfram `0`.
- Python **16 passed, 1 skipped** (로컬에서 원본 repo 전체 checkout 미존재로 Git blob check SKIP). **원격 CI에서는 실 원본 7/7 Git blob 검사를 실행해야 한다.**
- Full numeric eigenframe RHS와 7D constrained RHS의 492 상태, 2종 물리적으로 틀린 유체 ODE, 2종 angular-frame 부호 오류, oblique projector 함정 등을 검산했다. 독립 작성자/외부 심사는 NOT_RUN. 자세한 값은 `HOSTILE_REFEREE_KO.md`.

## R8–R10: Result, source provenance, computational contract and handoff

**승인:** class-A의 원본 perfect fluid Gauss·Codazzi 정확 전파 정리, regular VI0 7D full-vs-constrained dynamics의 source-owned local implementation, 순수 프레임 gauge scalar projector cancellation. **비승인:** full physical photon Liouville directions, polarized collision P8, 일반 비고유/퇴화 eigengauge, scalar oblique projector의 unitary Kato, arbitrary charged/ionized source, Type-II preflight/production migration, full VI0 branch atlas, observed CMB.

BASS upper 9/15 **scoped/source-mapped** (별도 과학 그래프), Join J1 **0/2 FULL PASS**, `G-DYN-MANIFOLD-VI0=PARTIAL`, `P-MIG-II-PREFLIGHT=OPEN`. New fully complete upper DAG nodes 0 and production nodes 0. `merge_ready=false`, production HOLD, `auto_next=false`. Source-protected parent PR310 그대로 유지.

**정확한 다음 이론 의무:** BASS 소스 `N,Sigma,R`가 주는 *물리적* photon direction flow `n'_phys`와 실제 angular quadrature grid transport를 회전 gauge에서 분리해 scalar/bath projector 전체 `dot P`를 구성한다. 다만 원래 Type-II **P-MIG-II-PREFLIGHT**도 병렬 독립 실행이 가능한, Join J1에 필요한 production 의무다. 이 문서의 코드와 그림은 둘 중 어느 production gate도 PASS로 승격하지 않는다.

**복사 가능한 후속 handoff:** `NEXT_HANDOFF.txt` 참조. 단계별 S0/S1/S2 GitHub+Library+Drive 게시 계보: `R1_R10_STAGE_LEDGER.json` 참조. 바이트 백업의 provider ACK와 복원 SHA는 별도로 기록한다.
