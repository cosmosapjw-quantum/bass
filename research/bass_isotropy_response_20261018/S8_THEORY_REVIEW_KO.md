# S8 독립 이론 검토: birth memory와 양의 angular refinement

이 문서는 S7의 완료 결과를 재사용하여 **새 S8의 full tangent와 native 각도 분해능**을 검토한다. S7 campaign은 다시 실행하지 않았다. 아래 kernel·KL·event 식은 직접 유도하고, 별도 표준 라이브러리 구현의 **Fraction 24개 + 90자리 Decimal 7개 검사**로 확인했다. 실제 S8 trajectory와 native accuracy의 판정은 별도 campaign receipt에 속한다.

## 1. 고정된 문제와 미분하는 family

Spacetime은 non-tilted axisymmetric Bianchi I, signature는 \((-,+,+,+)\)다.

\[
a_\perp=a e^{-b},\qquad a_\parallel=a e^{2b},\qquad
s=\dot b,\qquad \Sigma=\sqrt3|s|/H.
\]

S7의 닫힌 manufactured donor 계와 \(x=\ln(a/a_{\rm ref})\), \(h=H/H_*\), \(y=s/H_*\)를 그대로 쓴다. \(H_*\), 초기 에너지 성분, donor decay parameter, birth 일정은 고정한다. S8 tangent의 독립 parameter는 초기 signed shear \(p=y_0\)이고, 모든 parameter 미분은 **같은 \(x\)**에서 취한다. \(b_0\)는 고정된다. 이 계약은 실제 MD14 source의 native Einstein closure를 추가하지 않는다.

새 birth는 locally isotropic source라고 선언된 경우에만 보정한다. 기존 isotropic·physical anisotropic stock의 birth 방향·weights·양은 고정된다. 기존 stock의 **분포를 고정한다는 것과 현재 geometry 변화에 대한 에너지·stress 응답을 0으로 놓는 것은 다르다.** 후자는 잘못된 tangent다.

## 2. 직접 확인한 kernel partials

출생 \(u\)에서 관측 \(x\)까지 \(d=b(x)-b(u)\), 출생 source-frame cosine \(\mu\)를 쓴다. 다음을 정의한다.

\[
W=e^{2d}(1-\mu^2),\qquad V=e^{-4d}\mu^2,\qquad
R=\sqrt{W+V},\qquad D=(V-W/2)/R.
\]

미분은

\[
R_d=-2D,
\qquad
D_d=-\frac{W^2+14WV+4V^2}{2R^3},
\tag{S8.1}
\]

\[
R_\mu=\frac{\mu(e^{-4d}-e^{2d})}{R},
\qquad
D_\mu=\frac{\mu(e^{2d}+2e^{-4d})}{R}
-\frac{D\mu(e^{-4d}-e^{2d})}{R^2}.
\tag{S8.2}
\]

실제로 \(R_d=[W-2V]/R\)이고 \((V-W/2)_d=-4V-W\)다. 따라서 \(D_d\)의 chain-rule 식에 \(R^3\)을 곱하면

\[
(-W-4V)(W+V)+2(V-W/2)^2
=-\tfrac12(W^2+14WV+4V^2)
\]

가 되어 (S8.1)의 부호와 정규화를 독립 확인할 수 있다. 양의 \(R\)에서 \(D_d<0\)이며, \(\mu=0,\pm1\)도 정칙이다. \(d=0\)에서는 \(R=1\), \(D=P_2\), \(R_\mu=0\), \(D_\mu=3\mu\)다. S3의 이미 검증한 Legendre 전개를 새로 수행했다고 세지 않는다.

## 3. 움직이는 source-frame 방향과 prior

고정 reference ray label을 \(\nu_i\)라고 하면 실제 S7 `angular_balance.py::lrs_rule`은

\[
r_i(b)=\sqrt{e^{2b}(1-\nu_i^2)+e^{-4b}\nu_i^2},\quad
\mu_i=\nu_i e^{-2b}/r_i,\quad
q_i=\frac{w_i r_i^{-3}}{\sum_j w_jr_j^{-3}}
\]

를 사용한다. 여기서 직접

\[
\mu_{i,b}=-3\mu_i(1-\mu_i^2),\qquad
g_i:=\partial_b\ln q_i
=6\left(P_2(\mu_i)-\langle P_2\rangle_q\right)
\tag{S8.3}
\]

를 얻는다. 미분이 필요한 것은 단순한 \(d\)의 변화뿐 아니라, **새 birth에서 정한** \(\mu_i(b_u)\)와 \(q_i(b_u)\)의 변화다. Source-frame support/prior를 외부에서 고정한 다른 manufactured family에서는 이 두 미분이 0이므로 같은 family라고 섞어 해석하지 않는다.

## 4. 양의 KL projection의 implicit derivative

\(T_i=(P_2(\mu_i),P_4(\mu_i))\), 목표 \(\langle T\rangle_\alpha=0\)이고, 실제 `angular_p24.py`의 부호대로

\[
\alpha_i=\frac{q_i\exp(\lambda\cdot T_i)}
{\sum_jq_j\exp(\lambda\cdot T_j)}
\]

를 쓴다. \(T_{i,b}=T_{i,\mu}\mu_{i,b}\)이며

\[
T_{i,\mu}=\left(3\mu_i,\frac{35\mu_i^3-15\mu_i}{2}\right).
\]

\(\chi_i=g_i+\lambda\cdot T_{i,b}\)와 양의 weights에 대한 covariance
\(\mathsf V=\operatorname{Cov}_\alpha(T,T)\)를 정의한다. Normalized exponential의 미분은

\[
\alpha_{i,b}=\alpha_i\left[
\chi_i-\langle\chi\rangle_\alpha
+(T_i-\langle T\rangle_\alpha)\cdot\lambda_b
\right].
\tag{S8.4}
\]

제약 자체도 움직이므로

\[
0=\partial_b\langle T\rangle_\alpha
=\langle T_b\rangle_\alpha
+\operatorname{Cov}_\alpha(T,\chi)
+\mathsf V\lambda_b.
\]

따라서 구현할 식은

\[
\boxed{\mathsf V\lambda_b
=-\langle T_b\rangle_\alpha
-\operatorname{Cov}_\alpha(T,g+\lambda\cdot T_b)}.
\tag{S8.5}
\]

\(-\langle T_b\rangle\)를 빠뜨리면 고정된 equality matrix를 미분한 결과가 되어 틀린다. 독립 Fraction 검사의 해당 negative control은 실제 nonzero constraint derivative로 거절됐다. 구현에서는 근사 optimum의 \(\langle T\rangle\)를 0으로 하드코딩하지 않고 실제 mean으로 center한다.

이 식의 대상은 strict-interior full-rank의 **smooth ideal KL branch**다. 유한 허용오차로 중단하는 bisection의 분기 선택 자체가 미분 가능하다는 주장이 아니다. 실제 저장된 근사 optimum에서 식을 평가하고 정확한 moment admission·conditioning·독립 finite difference로 해당 범위를 검증한다. \(\mathsf V\)의 작은 eigenvalue나 큰 condition number는 derivative conditioning 실패로 분류한다. 이를 양의 해가 없다는 feasibility 정리로 바꾸지 않는다.

### Prior derivative의 식별성

현재 LRS prior에서는 상수항을 제외한 \(g=6P_2\)가 제약 feature span 안에 있다. (S8.4)–(S8.5)에 모두 일관되게 넣으면 이 항은 \(\lambda_{2,b}\)를 \(-6\)만큼 이동시키고 \(\alpha_b\)에서는 상쇄된다. 독립 Fraction 검사로 이 상쇄도 확인했다. 따라서 prior derivative를 식 전체에서 일관되게 생략하는 negative control이 반드시 다른 \(\alpha_b\)를 내야 한다고 요구하면 안 된다. \(\mu_b\), \(\alpha_b\), explicit birth-memory 항을 각각 빠뜨리는 S8 control은 다른 진단이다.

\(\alpha_b\)에는 양수와 음수가 모두 있어야 합이 0일 수 있다. 이는 signed derivative이며 물리적인 음의 weights를 사용하는 것이 아니다. 실제 양쪽 parameter family의 \(\alpha\)는 모두 양수여야 한다. Reflection parity는 \(\mu_b\)가 odd, \(\alpha_b\)가 even으로 유지된다.

## 5. Birth memory가 있는 cohort sensitivity

\(B(x)=\partial_p b(x)\), \(Y(x)=\partial_p y(x)\), \(J(x)=\partial_p h(x)\), \(B_k=B(u_k)\)라 쓰자. 이 parameter family에서는 \(u_k\)와 양의 출생 에너지 \(w_k\)가 고정이다. \(L_k=w_ke^{-4(x-u_k)}\)에 대해

\[
E_k=L_k\sum_i\alpha_{ki}R(d_k,\mu_{ki}),\qquad
\Pi_k=L_k\sum_i\alpha_{ki}D(d_k,\mu_{ki}).
\]

출생 이후 각 저장 배열은 불변이지만 서로 다른 parameter 해의 출생 배열은 다르므로

\[
\partial_p E_k=L_k\sum_i\left[
\alpha_iR_d(B-B_k)
+\alpha_iR_\mu\mu_{i,b}B_k
+\alpha_{i,b}R B_k\right],
\tag{S8.6}
\]

이고 \(\partial_p\Pi_k\)는 \(R\)를 \(D\)로 바꾼 식이다. Explicit memory \(-R_dB_k,-D_dB_k\), source-frame 방향, projection weights의 세 항을 구분한다.

기존 stock은 \(B_k=0\)이고 저장된 \(\alpha,\mu\)를 미분하지 않는다. 그 경우에도 \(\alpha R_d B(x)\), \(\alpha D_d B(x)\)는 남는다. 독립 Decimal fixture에서 고정 old distribution의 현재 geometry 에너지 derivative가 **0.0541249220…**로 0이 아님을 직접 확인했다. 이는 fixture 수치이며 실제 S8 cosmology의 관측값으로 재사용하지 않는다.

## 6. 독립 H 진화와 event sensitivity

고정 donor와 cosmological constant의 S7 식은

\[
b'=y/h,\quad y'=-3y+\Pi/h,\quad
h'=\frac{-h^2-2y^2-E_d/2-E_\gamma+L}{h}.
\]

따라서 \(\partial_pE_d=0\)인 현재 family의 tangent는

\[
B'=Y/h-yJ/h^2,
\quad Y'=-3Y+\Pi_p/h-\Pi J/h^2,
\]

\[
J'=(-2-h'/h)J-4yY/h-E_{\gamma,p}/h.
\tag{S8.7}
\]

초기 조건은 \(B(0)=0\), \(Y(0)=1\), \(J(0)=y_0/h_0\)이다. \(H_*\)는 parameter 변화에 따라 다시 정규화하지 않는다.

별도의 gauge control에서는 source-frame GL 방향과 weights를 고정한 채 현재와 모든 cohort의 birth \(b\)에 같은 상수 offset을 더한다. 이때 parameter를 그 offset으로 바꾸고 초기 조건을 \((J,B,Y)=(0,1,0)\)으로 둔다. 기존 cohort에도 \(B_k=1\)을 적용하므로 \(B-B_k=0\), \(E_{\gamma,p}=\Pi_p=0\)이고 \((J,B,Y)=(0,1,0)\)이 유지된다. 이는 위의 fixed-\(b_0\), \(p=y_0\) 연구 family와 구분된 symmetry control이다. 고정 reference-grid의 P24 rule에서 \(b_0\)만 바꾸는 유한 quadrature 실험을 같은 gauge test라고 부르지 않는다.

Birth에서 \(d=0\)이고 \(B(x)=B_k\)다. (S8.6)의 첫 항은 0이며, \(R_\mu(0)=0\), \(\sum_i\alpha_{i,b}=0\)이므로 \(E_{\mathrm{new},p}(u_k)=0\)이다. 마찬가지로

\[
\Pi_{\mathrm{new},p}(u_k)
=w_k B_k\left[\sum_i\alpha_{i,b}P_2(\mu_i)
+\sum_i\alpha_i3\mu_i\mu_{i,b}\right]=0.
\]

출생 event의 위치와 에너지 이전량이 parameter와 무관하므로 \(h,b,y\)와 \(J,B,Y\)는 event를 통과해 연속이다. RHS는 바뀔 수 있다. Event time이나 donor parameter를 미분하는 다른 family에는 이 설명을 그대로 적용할 수 없다.

Hamiltonian residual과 sensitivity는

\[
C=h^2-y^2-E_d-E_\gamma-L,\qquad
C_p=2hJ-2yY-E_{\gamma,p}.
\]

S7의 \(C'=-2C\)에 대응해 between-birth \(C_p'=-2C_p\), event \([C_p]=0\)이다. 독립 Fraction 검사에서는 constraint에 강제로 놓지 않은 일반 유리수 상태와 임의 variation을 사용해 이 identity를 확인했다. H를 constraint 값으로 덮어써서 residual을 0으로 만드는 검사는 아니다.

## 7. 실제 독립 검산

새 script는 `evidence_s8/theory_review/independent_tangent_checks.py`다. BASS, NumPy, SciPy, Rust, ODE, 기존 S7 테스트를 import하지 않는다. 정확한 양의 8-ray 유리수 fixture를 두 6-ray rule의 convex mixture로 구성하고, 새 이동 prior에 대한 별도 90자리 Decimal Newton solve와 대조했다.

| 검산 | 실제 결과 |
|---|---:|
| Fraction exact checks | 24 PASS |
| Decimal checks | 7 PASS |
| Kernel partial 중앙차분 최대 차이 | 2.3755524e−48 |
| Smooth positive-KL \(\alpha_b\), step1e−8 차이 | 2.9174557e−16 |
| Step1e−3 →5e−4 →2.5e−4 오차비 | 3.99991298,3.99997825 |
| Wall time | 0.0326초 |
| Peak RSS | 11008KiB |

실행 명령은 다음과 같다. 이 명령은 이미 수행했으므로 S8 재개 시 반복할 의무가 아니다.

```bash
python3 evidence_s8/theory_review/independent_tangent_checks.py \
  > evidence_s8/theory_review/INDEPENDENT_TANGENT_CHECKS.json
```

Script SHA-256은 `3aa9d7c3ab86d5d3c91fc195830ed90266bfeaec3e7d2c1c26a64949d3347fdd`, receipt SHA-256은 `dbfb82cb60431b164c84a5b4d266906250f9d7e39b9634982d0c22db1490b81e`다. 이는 분리한 구현·대수 검증 수준의 독립성이다. 실제 full tangent trajectory의 validation이나 일반 conditioning 보장을 대신하지 않는다.

## 8. Native n>32의 실제 owner API 검토

Pinned owner는 `rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177`다. 실제 파일을 읽어 다음을 확인했다.

- `axbi_sources.rs`: `AxbiSource`는 `Clone`이며 `angular_cells: Vec<AngularCell>`은 public이다. `angular()` 생성기의 허용값은8/16/32다. Private \(n_{H0}\), escape fraction과 spectral cells는 source clone에서 유지된다.
- `axbi_covariant_transport.rs::CovariantTransport::new`: angular 배열이 비지 않았는지 검사하고 실제 길이로 state를 할당한다. 이 활성 경로에는32 상한이 없다.
- `axbi_q_grid.rs::QFixedGrid::new`에는 별도의8/16/32 제한이 있으나 현재 native refinement의 활성 transport가 아니다. 이 cap을 모든 owner API의 cap으로 일반화하면 틀린다.

따라서 **기존32 source를 clone하고 새로 선언된 isotropic birth용 angular cells만 바꾸는 별도 wrapper**는 spectral owner를 편집하지 않고 추가 support를 사용하는 구체적인 경로다. 현재 `native_angular_refinement.rs` draft는 동일한 mirrored GL recurrence·Newton stop으로32 생성기의 bit 일치를 확인하고64/128/256을 확장한다. 유한·정렬·범위·strict positivity·정규화·parity를 새 wrapper가 직접 검사해야 한다. 일반 GL 이론은 이 생성 원리를 뒷받침하며, finite precision 구현의 전역 continuum accuracy를 보장하지 않는다.

원래 n32의 physical anisotropic stock은 원래 transport/grid에서 그대로 보유하고, 새 grid의 cohort와 **같은 관측 geometry·per-H normalization**에서 inventory/stress를 합산한다. Collisionless 선형 수송에서 이러한 별도 grid의 합산은 old 분포의 remesh가 아니다. 같은-grid synthetic incremental control은 별도 이름으로 기록해야 한다.

새 photon만의 \(\mathcal A\) 오차와 old+new total을 분리한다. Old 에너지로 denominator를 키워 new-source angular 오차를 작게 보이게 해서는 안 된다. 새로운64/128/256 결과는 기존32의 historical 내부 tolerance3e−15와도 구분한다. 새 runner의 내부1e−15가 최종 exact admission3/10^15를 완화한 것으로 해석되지 않게 source/prereg를 고정한다.

## 9. Dual-audit 판정과 실행 범위

**PHYS-MATH:** 식(S8.1)–(S8.7), moving equality 항, parity, 양의 smooth branch, fixed old distribution, fixed-x donor/event 계약을 직접 유도·검산했다. Prior-score cancellation은 negative-control 설계의 실제 조건으로 구현 담당자에게 전달했다.

**PHYS-MATH-CODE:** 실제 S7 plus-sign KL exponent와 `lrs_rule`, Duhamel diagnostic 범위, pinned owner constructor/transport를 읽었다. New tangent/native Python observer와 최종 frozen source의 검토 결과는 `evidence_s8/theory_review/`의 별도 receipt에 기록한다. 현재 이 문서만으로 두 S8 campaign을 PASS 처리하지 않는다.

원래 S7 R1/R2 FAIL, R3 한 이력 PASS, native1e−6 high-b 목표 FAIL은 원래 identity로 남는다. S8는 별도 증거를 추가한다. Native MD14 energy-supply/Einstein closure, evolving reactive history, production/full EoR/merge는 이 단위의 결과가 아니다. \(b_0\)는 고정 격자 기준 offset이며 물리 shear는 따로 \(s/H\) 또는 \(\Sigma\)로 표시한다.

## 10. 사용한 skill context

실제로 읽은 plugin은 **PhysMath Research Loop1.3.0**, package `c40/physmath-research-loop`다. 아래 resource를 사용했다.

```text
skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop/SKILL.md
skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop/references/POLICY_INTEGRATION.md
skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop/references/THEORY_LOOP.md — R6 definition
skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop/references/CODING_LOOP.md — C9 definition
skill://plugins_6acdfbba921881919e0c17843706aef4/physmath-research-loop/references/SUBAGENT_MODE.md
```

이 작업은 부모의 S8 단위에 대한 한 번의 상보적 R6/C9 검토다. 재귀 reviewer를 만들지 않았고, 새 과학 대상이나 승인 조건을 추가하지 않았다. 기존 identity를 재사용하고, 새 식을 판별하는 작은 검사와 현재 변경 표면만 확인했다.
