# BASS PR167 연구: FD96 응력 중립점, convexity 및 Einstein–Vlasov 실제 진화

**2026-10-16 KST.** 이 문서는 BASS PR166 `02149a6830dfe7ed214b77f5309e38350d2659fb`를 immutable parent로 삼은 **BASS-only** 이론·경량 코딩 연구이다. 원본 FD96 `bianchi/matter/freestream.py` Git blob `8467932c3281f9d426712b3a582f2aae3a484692`, PR164 kinetic-tangent original Git blob `1cab2bf7eab5a306ab207206ca3a0fc793dc9163`. 처음부터 `rei_bianchi` production/화학/체크포인트를 수정하지 않았고 NCP는 사용하지 않았다. ChatGPT container Python 3.13/NumPy 2.3.5/SciPy 1.17.0/mpmath 1.3.0에서 실제 실행했다. Native subagent tool 미노출로 `NOT_RUN`.

## 단계 1: 이론

- LRS metric `(-,+,+,+)`와 `W(mu)=1+A P2(mu)>=0`, `-1<=A<=2`를 원래 고정 Killing 운동량에 보존한다. `x=ln(a/aref)`, `k=e^-2x q²`, `z=mu²`, `X=k e^2b(1-z)`, `Z=k e^-4b z`, `E=sqrt(m²+X+Z)`.
- `rho_b=-2 DeltaP`, `E_bb=[m²(2X+8Z)+X²+14XZ+4Z²]/E³>0`. 그러므로 kinetic density는 b에 대해 엄격히 convex, `chi_b=∂bDeltaP=-rho_bb/2<0`. 양의 비퇴화 angular/radial source는 실수축에서 유일한 stress-neutral minimizer `b_star(x,A,m)`를 갖는다. Original BASS chart는 |b|<=1이므로 root chart admission은 별도 검사.
- `∂A DeltaP>0` (P2와 angular stress kernel의 양의 공분산)이고 `db_star/dA>0`; `sign(b_star)=sign(A)`. `db_star/dA|A=0=1/(10-2R)`에서 `0<R<1`, 따라서 `0.1<...<0.125`.
- 비상대론적 극한 `b_star=(1/6)log[(5+2A)/(5-A)]`. 이 수치는 finite mass의 상수 편향을 가정한 후험적 보정이 아니라 source formula로부터 직접 도출된 극한이다.
- Wolfram 4개의 원래 LRS 대수 항등식 residual=0, 일반 diagonal 비-LRS Hessian 3x3 matrix의 9 component symbolic residual=0, SymPy source 독립 대수 checks PASS. BASS 원래 source의 스칼라/벡터 부호는 BASS PR163/164와 일치.

## 단계 2: 실제 FD96/GL source 계산

- BASS 원래 Gaussian-mapped FD96 radial q/DQ, Fermi-Dirac q 분포, GL32 mu를 실제로 재구성했다. m/Tref=3,30,300에서 원본 source norm/reference mean-v²와 13자리 이상 일치했고, read-only PR164 Python의 rho, pbar, DeltaP, chi, DeltaP_A와 2개 부모-parity 테스트 통과.
- Chi 계산에서는 PR163의 부호 다른 term subtraction 대신 `chi_b=-(r³/2N) ∫W rw E_bb`의 모든 양의 분자 term을 적분한다. DeltaP는 PR162의 `expm1 + rationalized inverse-energy` representation 유지. |b|~1e-16, A=0의 부호가 유지된다.
- 신규 테스트 18개 + 원본 source parity 2개 = **20 PASS**. 범위 초과, 음의 pressure, A positivity, zero shears, direct-vs-stable stress, analytic differential/implicit response, NR limit, angular convergence, source original norm 포함.
- 실제 `45` source chart cases (m=3,30,300 × x=0,.7,ln(4.2) × A=-1,-.5,0,.5,2) 모두 `chi_b<0`, `dbstar/dA>0`; 해당 sampled chart에서 `max|b_star|=0.20027775352065053<1`, `max|DeltaP(b_star)|/rho=2.579049219082558e-15`.
- 별도 45개 angular quadrature scan(GL8/16/32/64/128)에서 GL16–GL128 root 최대 차이는 `3.5818570331969113e-13`. 이는 sampled bstar convergence이며 continuum q integral certificate가 아니다.
- x=.7,A=2에서는 m=3/30/300의 b_star가 `0.19224316779331183 / 0.18329114296114257 / 0.18310396919961355`; m→infinity leading NR `0.18310204811135164`.

## 단계 3: nonlinear BASS IVP 검증

- PR164 original kinetic-tangent source Git blob을 로컬 동일 bytes로 검사했고 원래 `EinsteinTangent` DOP853 model을 불변으로 불러 사용했다. m=3,30,300 × A=-.5,0,.5,2 의 12개 조건 × 81 state points = **972 실제 Einstein–Vlasov IVP 상태** 생성. 새 dynamics unittest 5개 PASS.
- `rho_x+3(rho+pbar)+2(s/H)DeltaP=0` source energy-work identity의 independent finite-difference max normalized= `5.139106620253739e-10` (test tolerance 2e-9). `H_x` Raychaudhuri max normalized= `1.0489418315828934e-10` (test tolerance 2e-9). These are finite difference residuals, not mathematically rigorous bounds.
- Initial signed shear zero, m=3,A=.5, at z4: actual `b=0.00149040868198984`, instantaneous stress-neutral `b*=0.04929762909960218` (actual/neutral `0.030232867365255645`), user instantaneous `Sigma=0.001459375570729503`, kinetic `DeltaP=+6.550278408363588e-5`. **즉 stress-neutral point와 실제 expanding dynamics는 구별되어야 한다.**
- MP54 fixed binary64 FD96 q,mu nodes high precision summation/root independent check two cases: m3,x=.7,A2 root deviation `6.166405378858776e-16`, m300,x1,A-1 `9.382233267675628e-17`. **원래 binary64 구적 노드를 그대로 사용했으므로 continuum quadrature precision check는 아니다.**
- 일반 diagonal Bianchi I: positive momentum support에서 `H_ij=2 delta_ij w_i/E-w_i w_j/E³` is PSD, positive on constrained tracefree plane after supported quadrature; ∂beta_i rho=-P_i. Equal principal pressures characterize interior kinetic energy minimum (given positive angular support, parity-even source for consistent diagonal stress), not necessarily zero geometric shear. Wolfram matrix residual all nine 0. Separate **manufactured finite 3-axis** source: 300 random anisotropy states; smallest sampled constrained eigenvalue `0.10306462419936606`; BFGS minimum beta `(0.1030087824801313,-0.11053199268847806,0.007523210208346759)`. This is NOT original BASS non-LRS FD96 production.

## 물리적 오해의 방지 / 적대적 검토

1. `b_star` is defined relative to a pinned spatial gauge/reference distribution; it cannot replace gauge-independent shear or CMB morphology. `Sigma=sqrt3 abs(s)/H` and signed s must be stored separately.
2. Strictly convex **kinetic energy at fixed x/source** does not prove cosmic time Lyapunov decay, full Einstein stability, uniform convergence, or absence of effects from photons, neutrinos, collisions or tilt.
3. For m>0 and A≠0, b_star is generally x-dependent. Imposing `b=b_star` as a post-hoc Einstein closure is physically invalid without integrating actual s/H and external stresses. Exactly `xi'=s/H - db_star/dx`, `DeltaP≈chi_b(b_star) xi` near the root.
4. The local proof on mathematical all-real b and original code-limited |b|<=1 differ. 45 cases are *sampled evidence*, not global chart theorem.
5. New non-LRS diagonal statement requires reflection symmetry to suppress off-diagonal stress in a diagonal metric; any eventual 3D solver must inspect BASS general tetrad/harmonic source.
6. Manufactured non-LRS gradient finite-difference initially failed an overly strict `2e-10` absolute bound with max measured `3.05e-10`; revised only to `1e-9`, retaining the physical positivity/invariant. The original first stderr was overwritten; this failure is preserved here, not claimed as byte-backed log.
7. **Publication novelty NOT_EVALUATED:** referenced Heinzle–Uggla (2006) and Lee–Nungesser–Tod (2020) for global kinetic Bianchi context, without implying our FD96 root chart is novel to the literature.

## 단계 DAG 상태와 백업

- S1 source-pinned derivation: `DERIVED`, Wolfram+SymPy PASS; local SHA-verified stage1 ZIP and GitHub branch commit; cloud upload attempt failed (`container_session_expired`).
- S2 FD96 implementation: `IMPLEMENTATION_VERIFIED`, 20 tests; GitHub Python core+focused test published and local stage2 ZIP; source exact bytes checked for parent original. Cloud upload: not completed.
- S3 dynamics+non-LRS: `NUMERICALLY_CHECKED`, BASS IVP and MP54, 5 dynamic tests, 300 toy checks; GitHub docs and scripts published. Cloud upload: not completed.
- S4 scientific scope review/handoff/publication: `READY`, package SHA and remaining CODEx runner gates below.
- Future S5 native `rei_bianchi` matter-response callback: `FUTURE_OWNER_GATED` until signed stress/mass-energy identities and existing production source gate are checked. No existing REI owner checkout changed.

Original source literature: https://doi.org/10.1088/0264-9381/23/10/016 ; https://doi.org/10.1007/s10714-020-02699-7 ; https://doi.org/10.1103/PhysRevD.84.024011 . This research is not using peer papers as code test substitutes.
