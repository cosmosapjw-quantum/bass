# FA03 C9: 적대적 정리·코드 감사와 유한 오차의 실제 수치 검사

2026-10-15 KST, 선택된 coding stage **C9** (실제 수학·코드·성능 감사), 부모 source commit 6812bac3148afa292189f0bdec3e5994a5b892b0. 이 연구는 사용자 Ubuntu 24.04에서 별도 local Codex 없이 직접 구현·실행했다. Git worktree를 분리하여 동일한 원본 FA02/FA03 데이터와 원본 C5–C8 이론·수치 산출물은 변경하지 않았다. Native subagent tool이 노출되지 않아 native_subagent=NOT_RUN이며, 독립 구현/정확 유리수/CAS 검증은 외부 peer review가 아니다.

## 1. BLOCK_NOW finding C9-F01: 잘못 명세된 C8 부동소수점 가중합 계약

C8 aggregation_roundoff.py는 각 sample의 가중합을 \(\gamma_N=Nu/(1-Nu)\) 형태로 추산하면서, 실제 tensor product 가중합의 두 번의 곱셈과 NumPy einsum의 구현-비공개 덧셈 순서를 명시하지 않았다. 이 \(\gamma_N\) 숫자를 **실제 einsum 전체의 이진수 오차상계로 인증한 주장은 철회해야 한다**. 이는 C8 GL4의 *정확한 연속 시간 ODE 에너지 구적 정리*를 반박한 것이 아니다.

정확한 IEEE754 binary64 입력에 대해, 어떤 한 sample \(s,w_r,w_e>0\)의 입력값이 모두 1보다 작을 때조차 \(\mathrm{fl}(\mathrm{fl}(w_rs)w_e)\)의 상대 오차가 \(\gamma_1\)보다 커질 수 있다. 실제 찾은 예:
- w_r = 0.9412270713189991
- w_e = 0.5406840691765105
- s = 0.3222052946869389
- actual two-multiplication relative error / \(u=2^{-53}\) = **1.3564588008572758**, 따라서 단일 \(\gamma_1\) 상계를 위반하되 \(\gamma_2\) 안이다.
- source exact: Fraction.from_float()를 사용해 각 binary64 입력값과 실제 \((w_r w_e)s\) 사이의 차이를 완전 유리수로 계산, 임의 허용오차 상향 없음.

이 반례는 **N=1의 일반 triple-product 모델에 대한 반례**다. 따라서 C8의 실제 36×GL4=144 terms 출력이 \(\gamma_{144}\)를 실제로 위반했다고 주장하지 않는다. 문제는 단순 연산 경로가 명세되지 않은 채 그 숫자를 보편적으로 인증한 과잉 주장이었다.

## 2. FIXED / source-locked 새 결정적 집계 검증 경로

deterministic_reducer.py의 pairwise_tensor_sum는 정확히 다음 순서를 수행한다:
(1) \(\mathrm{fl}(s\,w_e)\) (2) \(\mathrm{fl}(\mathrm{result}\,w_r)\)
(3) \(N=n_r n_e\) sample을 zero-padding한 \(\lceil\log_2N\rceil\) 깊이의 binary pairwise tree.
배열 레이아웃과 좌우 자식 덧셈 순서가 코드에 명시되어 있어 불명확한 einsum contraction order를 오차정리의 가정으로 숨기지 않는다.

가중치는 실제 입력 float64의 정확한 dyadic 유리수로, \(W=(\sum_r w_r)(\sum_e w_e)\)를 Fraction 합산하며, \(M=\max_{\epsilon,r,e,k}|S_k|\)도 정확한 float64 입력의 dyadic 유리수 최대를 취한다. 정상 IEEE rounding·no underflow/overflow, 온전히 **이미 계산 완료된 입력 배열 S**의 오류만을 대상으로, 각 Stokes component와 합성한 Jones/coherency의 초기 reconstruction 전 오차는
\[
 \boxed{|\Delta S_k|\le M W\gamma_{2+\lceil\log_2N\rceil},\quad
 \|\Delta F\|_1\le 4MW\gamma_{2+\lceil\log_2N\rceil}.}
\]
이는 서로 다른 Pauli/identity 2×2 기저 \(F=\frac12(I\mathbf1+Q\sigma_3+U\sigma_1+\cdots)\)에서 각 \(\frac12\sigma\)의 Schatten1-norm이 1인 것을 사용한다. 실제 부호가 섞인 Q/U/V도 절댓값을 통해 상계한다.

중요한 제외: (a) FA03 광선별 RK4 물리/roundoff 오차, (b) Legendre 노드와 가중치의 수치 생성 오차, (c) 반환 Stokes에서 복소 Hermitian \(F\)를 생성할 때 추가되는 binary64 덧셈, (d) 실제 C7의 opaque einsum contraction. 따라서 위 수치는 **새 pairwise 가중합 경로에 한정된 완전 지정 conditional theorem**이다.

실제 GL4+128 RK4 입력의 \(\|\Delta F\|_1\) 조건부 집계 상계:
| rays | N | tree height | \(\gamma\) operations | bound |
|---:|---:|---:|---:|---:|
|36|144|8|10|2.3263e-15|
|144|576|10|12|2.7916e-15|
|480|1920|11|13|3.0242e-15|

이 숫자는 C8에 기록된 old einsum-용 36ray3.952e-14/480ray5.270e-13 수치를 소급해서 증명하는 값이 아니다. 별개 알고리즘의 더 작은 conditional certificate이다.

## 3. 실제 이산 물리 해와 정확한 유리수 오라클

C7의 실제 source-locked 4-real-Stokes RK4를 사용하되, 마지막 단계를 통과하기 전 ray×energy 상태를 보존해 새 집계를 적용했다. ε=(-.1,0,.1), GL4, 128 RK4 steps, GL3×12/GL6×24/GL10×48. NumPy einsum, deterministic pairwise, math.fsum을 **동일한 물리 상태 배열**에 적용하고 정확한 유리수 원래 입력 합으로 비교했다.

| rays | NumPy einsum max Stokes abs exact-dyadic error | pairwise | math.fsum |
|---:|---:|---:|---:|
|36|2.3264e-17|5.0259e-17|2.3264e-17|
|144|4.3872e-17|1.2947e-17|1.2947e-17|
|480|4.7791e-17|3.6820e-17|1.8691e-17|

따라서 pairwise가 **항상 더 정확하다는 주장은 성립하지 않는다**. 실제 새 경로의 Fraction-based error inequality와 R7 frozen Jones solver, C7 real-Stokes 소스 결과 사이의 회귀 테스트는 통과했다. ε 독립 1/2/3-thread pairwise 병렬 출력을 실제 실행했으며 비트 단위로 같았지만, 480-ray microbenchmark reduction only 중앙값 각각0.208ms/0.608ms/0.793ms로 멀티스레드가 더 느렸다.

Matched full source GL4+128 RK4 wall median(5 warmed repetitions):
| rays | C7 original real Stokes | C9 pairwise | C9 math.fsum |
|---:|---:|---:|---:|
|36|0.03820s|0.04023s|0.04384s|
|144|0.06725s|0.06684s|0.08672s|
|480|0.15362s|0.17015s|0.15656s|

기본 production 연구용 경로는 **기존 C7 벡터화, workers=1**이다. 새로운 C9 경로는 수치 소급/정밀도 감사에 사용한다. 480-ray 가중합만의 tracemalloc peak는 NumPy einsum 186389 bytes, pairwise 628728 bytes, 따라서 메모리 감소 주장은 하지 않는다. 최고 480ray GL4 전체 C8의 10.85배 가속과 단일 worker 선택은 영향받지 않는다. 이전 C7의 full Jones/real Stokes 비교를 다시 측정했다고 주장하지 않는다.

## 4. ENERGY spectral theorem C8: audited and retained, with exact scope

C8 physical frozen source k=Lx^{-2/3}v and observer \(\chi=1/125\)를 원본 R7 source bytes와 실제 비교했다. \(k\le202/125,\ \operatorname{Re}(1+\epsilon(e k-1))\ge411/625\) for |e-1|≤1/2 and real |ε|≤1/10. Wolfram15.0.1 returned exact positive inequality and the 2×2 complex-energy generator identity \(G+G^\dagger=2\mathrm{Re}\alpha H\), all zero residuals. The *analytic* extension of the original matrix equation uses \(U(e)B(e)U(e)^T\), not \(U(e)B(e)U(e)^\dagger\). Switching to conjugate transpose would break holomorphy in complex e and invalidate the Taylor/Gauss proof. The 2-norm contraction of U and U^T follows because transpose preserves singular values, even at complex energy.

Hence the exact ODE normalized energy GLn trace bound \((41931/9600)25^{-2n}\) stands under its original **finite real-ray toy** scope, not full EoR chemistry. New completely independently coded mpmath70 positive constant H model (the original P3 physical Hermitian 2×2 block, H diag(.2,.4), same e/ε/source algebra, exact analytic time flow) evaluates the true normalized energy integral via highprecision quadrature and GL2/3/4/5/6/8. Three k,epsilon cases at (1.0,-0.1), (1.3,+0.1), (1.615,+0.1) produce 18 independently validated GL errors inside C8 bound. As representative, k=1.615 ε=.1 GL4 actual trace error \(3.8883148711\times10^{-25}\) compared with C8 conservative bound \(2.8624896\times10^{-11}\). This validates the algebraic mechanism for a constant-coefficient test, **not** a high-precision whole Bianchi-I time-dependent integration oracle.

Original R8 fixed36ray trace norm <4.75e-7 remains unchanged and scope-limited. Complex angular-strip propagated M4, radial GL3 validation, original FA03 true time-dependent RK4 enclosure, complete binary64 source/provider error and full reionization history all remain HOLD. The C8 Fraction manufactured constant-coefficient Hermite residual also remains valid within its stated constant-coefficient scope, not reinterpreted as full RK4 bound.

## 5. xAct + scientific source checks

Native Wolfram Engine15.0.0/xTensor1.3.0 was run locally (no Codex) on xact_c9.wl, EXIT0: seven exact zero covariant identities (screen rank2, observer/transverse null ray, projector square, photon-null and normal-frame energy sign). These are conventional physical consistency checks, not a proof of floating-point arithmetic.

Primary relevant mathematical sources: Nicholas J. Higham, *The Accuracy of Floating Point Summation* (SIAM J Sci Stat Comput 1993, original PDF https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf) and *Notes on Accuracy and Stability of Algorithms in Numerical Linear Algebra* (https://nhigham.com/wp-content/uploads/2023/10/high99n.pdf); Eric Hallman and Ilse Ipsen, *Deterministic and Probabilistic Error Bounds for Floating Point Summation Algorithms* (arXiv:2107.01604). These motivate correct bounded operation trees; none assert BASS-specific measured outcomes.

Latest cross-repo source reading: bass_cr PR70 source-shape-free moment hulls reveal HeI uncertainty 6.8% for one frozen cold source at 256-grid (far larger physics-scope uncertainty than tiny FA03 toy spectral norm), BASS_HE PR62 conditional warm sixth-cell Fraction Bernstein fast caches, REC PR90 original HyRec/RATE parity and underflow-zero rate correction, WU088_HH PR77 radial cusp/interface interval accounting. These are independent physical inputs, not imported into FA03 and not a scalar multiplier on C8 toy errors. Latest rei_bianchi readback HEAD 2c3e5accace90856eb6c4fe7f0030a7ace584e91, AX07 scoped conditional COMPLETE, AX08 IN_PROGRESS, AX11 and AX12 PENDING, scientific_admission NOT_ISSUED. Owner worktree and processes **not modified/started** by this BASS C9 run.

## 6. Review decisions

- C9-F01 **BLOCK_NOW → FIXED_SCOPED**: C8 gamma_N general guarantee for tensor product float einsum cannot be admitted; positive exact binary64 triple-product witness, new explicit pairwise operation graph, correct gamma tree-depth and Fraction source contract, actual regressions and source-bound outputs. Old C8 source remains archived/byte-identical as historical, but the unsafe proof should not be cited as an admitted bound for NumPy einsum.
- C9-F02 **RETAIN**: exact finite-ray GLn normalized energy theorem with complex G Hermitian part and holomorphic transpose, input source SHA and independent mpmath test.
- C9-F03 **RETAIN_SCOPE**: C8 manufactured Hermite residual is true only for constant H, no false claim of actual time variable solver admission.
- C9-F04 **HOLD**: true production complex phi strip M4, radial GL3 continuum angular integration, full IEEE provider/ODE, H/He photo-history.
- C9-F05 **BACKLOG_NONBLOCKING**: additional optimized pairwise/compensated reduction might improve performance at larger rays, but measured 36–480 workload does not justify switching from C7 one-worker fast baseline.

C9 hostile internal review+actual numerical and CAS reproduction **COMPLETED_SCOPED**. Independent external scientist/another native agent NOT_RUN. Next coding stage is C10 scoped release/claim decision only when explicitly requested. No new user approval demanded for ordinary source/audit repair. All raw failed/positive evidence and runnable code preserved.
