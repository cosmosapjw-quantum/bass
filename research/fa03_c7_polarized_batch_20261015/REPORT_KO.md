# FA03 C7: 물리 일치성 검증과 실제 CPU 최적화

2026-10-15 KST. 선택 단계: physmath-research-loop coding C7. 이전 C6 commit 76cfa950a6504a219365b31e9358dec9e4c05f66의 별도 worktree에 추가 코드를 실제 작성·실행했다. 사용자의 지시에 따라 별도 local Codex 없이 ChatGPT에서 코딩했다. Native subagent는 현재 host에서 호출 도구가 없어 NOT_RUN.

## 동결 물리와 유도

Kasner Bianchi I, metric (-,+,+,+), x=t/to in [1/2,1], zero incoming coherency, observer chi=1/125, psi=1/100, cap radius delta=1/50rad, e=Ew/E* in [49/50,51/50] 그리고 |epsilon|<=1/10이다. Original FA02 and FA03 SHA256 1e89e75f7a08d2eec1851a58e602c2683b1888a37b3e1fe10b1be4234756eee5, ad865127da7c2f9ea613541571f9b842f9da7630af9bb951a3df5968ad44ecf7 are immutable. Absorption only depends on non-grey epsilon. Source P3 and K3 are original.

Let G=alpha H+omega J, H=.5 S^T K3 S positive, J=[[0,-1],[1,0]] antisymmetric, alpha=1+epsilon(e k-1). The exact 2x2 Hermitian coherency equation is
\[
\frac{dF}{dx}=B-GF-FG^\top,\quad B=e^3(1+0.1 e k) S^\top P_3 S.
\]
P3 has nonzero principal-block determinant 79/400>0, eigenvalues (0,0.270871215252...,0.729128784748...). Along the specified ray family k=x^(-2/3)v with x<=v<=1, so
\[
k\in[x^{1/3},x^{-2/3}],\quad
\alpha\ge\frac{11}{10}-\frac{51}{500}2^{2/3}
=0.9380850926992438>0 .
\]
This proves positive source and passive attenuation at every admitted epsilon and ray. For U(x,s) the exact Jones evolution satisfying dU/dx=-G U,
\[
F(x)=\int_{1/2}^{x} U(x,s)B(s)U(x,s)^\dagger ds .
\]
With zero incoming matrix it is Hermitian positive semidefinite. This is a property of the exact finite-energy ODE, not an interval proof that every RK4 intermediate preserves positivity.

Because G+G^T=2 alpha H, the screen rotation cancels from the trace:
\[
I'=I_B-2\alpha\,\mathrm{tr}(HF).
\]
Writing H=[[h0+hz,hx],[hx,h0-hz]] and F=1/2[[I+Q,U-iV],[U+iV,I-Q]], the EXACT real Stokes system is
\[
\begin{aligned}
I'&=B_I-2\alpha(h_0I+h_zQ+h_xU),\\
Q'&=B_Q-2\alpha(h_0Q+h_zI)+2\omega U,\\
U'&=B_U-2\alpha(h_0U+h_xI)-2\omega Q,\\
V'&=B_V-2\alpha h_0 V.
\end{aligned}
\]
No weak-polarization approximation. The cached fused six-state epsilon-zero RHS and finite-epsilon energy-resolved Jones and real-Stokes solvers are physically separate representations of this same frozen source.

## 실제 코드

The original fa02.py/fa03.py files were not edited. New standalone files:
- batch_transport.py: six-state moment fusion, shared three-point RK4 geometry, vectorized Jones finite-epsilon and bounded optional ray chunks, deterministic ThreadPoolExecutor ray parallelism.
- stokes_vector.py: exact 4-real Stokes representation, batched observer-ray x photon-energy x epsilon, half the nominal state-buffer bytes of complex128 Jones. Uses cached RK4 coefficients.
- test_c7.py and test_stokes.py: 19+15 = 34 new tests, actual source and RHS comparison against immutable reference, physical Stokes PSD cone, exact O(2) screen basis covariance, source SHA mismatch refusal, altered sign detection, convergence and deterministic threads.
- benchmark_c7.py, benchmark_stokes.py, plot_c7.py: runnable source-matched medians and plots, no invented speedups.

Actual local Ubuntu, Python3.12.3, NumPy2.4.2, steps64, energy GL8, signed eps(-.1,0,.1), median of 3 warmed actual timings:

| rays | original 3 separate Jones (s) | complex-fused (s) | real-Stokes (s) | real speedup |
|---:|---:|---:|---:|---:|
|36|0.10191|0.04720|0.02118|4.81x|
|144|0.29258|0.22510|0.04971|5.89x|
|480|0.77723|0.79367|0.09696|8.02x|

At 480 rays real-state nominal storage is 368640 bytes versus 737280 bytes for the same complex Jones state. This is state-buffer storage, not whole process RSS. Actual two-thread 480-ray median 0.18252 seconds and four-thread 0.34538 seconds, hence both SLOWER than one real Stokes batch; default workers=1. Optional bounded ray chunks trade speed for memory. The actual output comparison has source-matched trace norm differences <=3e-12 by benchmark acceptance and tighter test checks.

## CAS and validation evidence

Connected Wolfram15.0.1 algebra: antisymmetric J+J^T=0, G+G^T-2alphaH=0, Stokes eigenvalues (I±sqrt(Q²+U²+V²))/2, trace balance residual0, P3 principal minor79/400; passivity TRUE under physical domain. Native /usr/bin/wolframscript Wolfram15.0.0 and xAct xTensor1.3.0: 7 exact zero residuals for screen rank, transverse observer/photon, screen idempotence, photon-null, observer rest energy; local exit0. External independent reviewer and native subagent NOT_RUN.

The first 19-test run exposed a central difference epsilon step=0.02 truncation error 1.33002837e-9 exceeding the predeclared 1e-9 target; it was fixed by reducing epsilon step to 0.01 without widening acceptance. Then 19/19 PASS. New real-Stokes test 15/15 PASS. Inherited C5 15 and C6 18 must also pass before final release. All tests are scoped to frozen source and do not certify full REI chemistry.

## Existing certificates and related projects

The historical R8 fixed36ray finite-detector trace-norm error <4.75e-7, eigenvalue margin >0.12548, frozen six-matrix epsilon-zero closure and R5-R10 I–VII assumptions are unchanged. This optimized code makes NO claim about exact continuous angular cap error, true finite-epsilon six-moment closure, empirical atomic opacity or full reionization histories.

Relevant live separate repos: rec_bianchi PR88 already uses exact conserved Killing-momenta vectorization with optional threads, which its measured workloads found slower. bass_cr PR67 already has threshold-aware cohort and NumPy absorber/heat acceleration, parallel forkserver was slower. BASS_HE PR59 carries full warm P01 photon errors through its third saved cell, a different physics lane. WU088_HH PR74 screened output is likewise a separate lane. These are methodology comparisons, not source-rates imported to FA03.

rei_bianchi HEAD at readback 129627969dae18958ceef520c197bfa8b20b8888, native Rust owner tree has tracked modification of lib.rs; goal IN_PROGRESS, AX07 scoped ZERO complete, AX08 IN_PROGRESS, AX11/AX12 PENDING, scientific admission NOT_ISSUED. This BASS implementation did not modify its worktree, scheduling, or native solver.

## Decision and next

C7 physical science validation adopted for the specified fixed spectral/observer source, plus actual measured optimization. C8 remains READY_NOT_EXECUTED for authenticated angular, time, roundoff and source-provider error budgets, particularly propagated strip norm M4, radial GL3 remainder and convergence. No automatic subsequent C8 or production merge has been executed.